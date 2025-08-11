"""
A companion for developing Omnata Plugins, including generation of test cases with application request mocking.
"""

import datetime
import json
import os
import re
import copy
from typing import Any, Dict, List, Optional, Tuple, Union

import click
import pandas
import vcr
from omnata_plugin_runtime.api import (
    InboundSyncRequestPayload,
    OutboundSyncRequestPayload,
)
from omnata_plugin_runtime.configuration import (
    InboundSyncConfigurationParameters,
    OutboundSyncConfigurationParameters,
    StoredConfigurationValue,
    StoredMappingValue,
    SyncConfigurationParameters,
    SyncDirection,
)
from omnata_plugin_runtime.omnata_plugin import (
    InboundSyncRequest,
    OmnataPlugin,
    OutboundSyncRequest,
    SyncRequest,
)
from omnata_plugin_runtime.logging import OmnataPluginLogHandler
from pydantic import TypeAdapter
from pydantic_core import to_jsonable_python
from slugify import slugify
from .utils import get_snowpark_session
from snowflake.snowpark import Session
from tabulate import tabulate


def scrub_secrets(connection_secrets: Dict[str, StoredConfigurationValue]):
    """
    A secret scrubber for pyvcr, to redact the parts of the HTTP request which came from connection secret values
    """

    def before_record_response(request):
        for secret_name, secret_value in connection_secrets.items():
            if request.body is not None:
                try:
                    request.body = (
                        request.body.decode("utf-8")
                        .replace(secret_value.value, "[redacted]")
                        .encode("utf-8")
                    )
                    if secret_value.metadata is not None:
                        for (
                            metadata_secret_name,
                            metadata_secret_value,
                        ) in secret_value.metadata.items():
                            request.body = (
                                request.body.decode("utf-8")
                                .replace(metadata_secret_value, "[redacted]")
                                .encode("utf-8")
                            )
                except UnicodeDecodeError as unicode_decode_error:
                    # sometimes we're not dealing with plain text, e.g. uploading a zip file
                    pass
        return request

    return before_record_response


class SyncScenario:
    """
    Represents a scenario where we sync some data to an app, while capturing records and traffic
    """

    def __init__(
        self,
        plugin_id: str,
        scenario_name: str,
        sync_direction: SyncDirection,
        configuration_parameters: SyncConfigurationParameters,
        sync_request: SyncRequest,
        scenario_records: Optional[pandas.DataFrame],
        initial_stream_state: Optional[Dict] = None,
    ):
        self.scenario_name = scenario_name
        self.sync_direction = sync_direction
        self.configuration_parameters = configuration_parameters
        self.sync_request = sync_request
        self.scenario_slug = slugify(scenario_name)
        self.scenario_cassette_file_name = f"{plugin_id}_{self.scenario_slug}.yaml"
        self.scenario_cassette_file = os.path.join(
            "features", "vcr_cassettes", self.scenario_cassette_file_name
        )
        # create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.scenario_cassette_file), exist_ok=True)
        self.inbound_results_file_name = f"{plugin_id}_{self.scenario_slug}_results.csv"
        self.inbound_results_file = os.path.join(
            "features", "inbound_results", self.inbound_results_file_name
        )
        os.makedirs(os.path.dirname(self.inbound_results_file), exist_ok=True)
        self.scenario_records = scenario_records
        self.results:Optional[pandas.DataFrame] = None
        self.initial_stream_state = initial_stream_state


class DevelopmentSession:
    """
    Connects to Snowflake and manages test case related concerns
    """

    def __init__(
        self,
        omnata_app_name: str,
        plugin_instance: OmnataPlugin,
        recorded_http: bool = True,
        inject_snowpark_session: bool = False,
        plugin_module_override: Optional[str] = None,
    ):
        self.sync_slug = None
        self.results_dataframe = None
        # records property represents the latest record state (net result of all operations)
        self.records = None
        self.omnata_app_name = omnata_app_name
        self.feature_filename = None
        self.cassette_filename = None
        self.plugin_instance = plugin_instance
        self.plugin_module = (
            self.plugin_instance.__module__
            if plugin_module_override is None
            else plugin_module_override
        )
        self.vcr = None
        self.recorded_http = recorded_http
        self.inject_snowpark_session = inject_snowpark_session
        self.stream_index_fields:Dict[str,str] = {}
        self.stream_excluded_fields:Dict[str,List[str]] = {}
        self.exclude_records_by_field_value:Dict[str,str] = {}
        self.plugin_id = plugin_instance.get_manifest().plugin_id
        self.feature_filename = os.path.join("features", f"{self.plugin_id}.feature")
        self.current_scenario = None
        self.recorded_scenarios: List[SyncScenario] = []
        self.failed_source_records = None
        self.run_id = 0
        self.api_limits = None
        self.vcr_filter_query_parameters: List[str] = []

    def fetch_record_state(self):
        """
        Collects the full set of records which were previously staged
        """
        return self.current_scenario.scenario_records
    
    def set_inbound_stream_index_field(self,stream_name:str,index_field:str):
        """
        Sets the field to be used as the index field for a given stream.
        By default, it is set to the primary key field of the stream, but this may
        need to be overridden by a more stable identifier when testing against some
        live systems.
        """
        self.stream_index_fields[stream_name] = index_field

    def exclude_inbound_result_fields(self, stream_name: str, field_names: Union[str,List[str]]):
        """
        Excludes a field from the comparison of inbound results.
        """
        if stream_name not in self.stream_excluded_fields:
            self.stream_excluded_fields[stream_name] = []
        if isinstance(field_names,str):
            self.stream_excluded_fields[stream_name].append(field_names)
        else:
            self.stream_excluded_fields[stream_name].extend(field_names)
    
    def exclude_inbound_result_records_by_field_value(self, field_name: str, field_value: str):
        """
        Excludes records from the comparison of inbound results where the field matches the value.
        """
        self.exclude_records_by_field_value[field_name] = field_value

    def prepare_outbound_scenario(
        self,
        scenario_name: str,
        input_dataframe: pandas.DataFrame,
        parameters: OutboundSyncConfigurationParameters,
    ):
        """
        Prepares an outbound sync scenario using entirely client-side generated information.
        The input dataframe must be in the standard outbound record stare format, and
        all parameters must be provided, including connection parameters and secrets,
        sync parameters and field mappings.
        """
        outbound_sync_request = OutboundSyncRequest(
            run_id=None,
            session=self.session,
            source_app_name=None,
            records_schema_name="",
            records_table_name="",
            results_schema_name="",
            results_table_name="",
            plugin_instance=self.plugin_instance,
            api_limits=self.api_limits,
            rate_limit_state_all={},
            rate_limit_state_this_sync_and_branch={},
            run_deadline=None,
            development_mode=True,
        )
        outbound_sync_request._prebaked_record_state = input_dataframe

        self.current_scenario = SyncScenario(
            plugin_id=self.plugin_id,
            scenario_name=scenario_name,
            configuration_parameters=parameters,
            sync_direction=SyncDirection.OUTBOUND,
            sync_request=outbound_sync_request,
            scenario_records=input_dataframe,
        )

        self.plugin_instance._sync_request = outbound_sync_request
        if self.recorded_http:
            self._start_recording()
        return parameters, outbound_sync_request

    def prepare_outbound_scenario_from_sync(
        self, scenario_name: str, sync_slug: str, snowcli_environment: str = "dev"
    ) -> Tuple[OutboundSyncConfigurationParameters, OutboundSyncRequest]:
        """
        Prepares an outbound sync scenario using a Sync which has been fully configured in the Omnata app.
        The user must have the Omnata application role PLUGIN_DEVELOPER, as well as having develop privileges
        on the plugin app.
        """
        # first, check to see if there's no click context, happens in Jupyter notebooks
        if not click.globals.get_current_context(silent=True):
            # set an empty one so snowcli's app config doesn't error
            click.globals.push_context(click.core.Context(click.core.Group()))
        self.session: Session = get_snowpark_session(connection_name=snowcli_environment)
        self.sync_slug = sync_slug
        session_run_response = self.session.sql(
            f"""
            call {self.omnata_app_name}.API.CREATE_DEVELOPMENT_SESSION_RUN('{sync_slug}')
            """
        ).collect()
        response_parsed = json.loads(session_run_response[0][0])
        if response_parsed["success"] is False:
            raise ValueError(f"Failed: {response_parsed['error']}")
        response_data = response_parsed["data"]
        if "direction" not in response_data:
            raise ValueError(
                f"Invalid response from CREATE_DEVELOPMENT_SESSION_RUN: {response_data}"
            )
        if response_data["direction"] != "outbound":
            raise ValueError("The provided sync is not an outbound sync")
        if "outbound_apply_payload" not in response_data:
            raise ValueError(
                f"Invalid response from CREATE_DEVELOPMENT_SESSION_RUN: {response_data}"
            )
        if "plugin_app_name" not in response_data:
            raise ValueError(
                f"Invalid response from CREATE_DEVELOPMENT_SESSION_RUN: {response_data}"
            )
        plugin_app_name = response_data["plugin_app_name"]
        outbound_payload = OutboundSyncRequestPayload.model_validate(
            response_data["outbound_apply_payload"]
        )
        # we have everything we need except the secrets, which we fetch from the plugin app
        oauth_secret_param = (
            f"'{outbound_payload.oauth_secret_name}'"
            if outbound_payload.oauth_secret_name
            else "null"
        )
        other_secrets_param = (
            f"'{outbound_payload.other_secrets_name}'"
            if outbound_payload.other_secrets_name
            else "null"
        )

        secrets_fetch_response = self.session.sql(
            f"""
            call {plugin_app_name}.PLUGIN.RETRIEVE_SECRETS({oauth_secret_param},{other_secrets_param})
            """
        ).collect()
        secrets_response_parsed = json.loads(secrets_fetch_response[0][0])
        if secrets_response_parsed["success"] is False:
            raise ValueError(f"Failed: {secrets_response_parsed['error']}")
        secrets_data = TypeAdapter(
            Dict[str, StoredConfigurationValue]).validate_python(secrets_response_parsed["data"])

        source_database = self.omnata_app_name
        source_schema = outbound_payload.records_schema_name
        source_table = outbound_payload.records_table_name
        full_source_table_name = f"{source_database}.{source_schema}.{source_table}"
        source_table = self.session.table(full_source_table_name)
        self.api_limits = outbound_payload.api_limit_overrides
        # self.api_limits.concurrency = 1 # we have to set this because pyvcr isn't thread safe
        scenario_records = pandas.DataFrame(source_table.collect())
        configuration_parameters = OutboundSyncConfigurationParameters(
            connection_method=outbound_payload.connection_method,
            connection_parameters=TypeAdapter(
                Dict[str, StoredConfigurationValue]).validate_python(
                outbound_payload.connection_parameters,
            ),
            connection_secrets=TypeAdapter(
                Dict[str, StoredConfigurationValue]).validate_python(secrets_data
            ),
            sync_parameters=TypeAdapter(
                Dict[str, StoredConfigurationValue]).validate_python(outbound_payload.sync_parameters
            ),
            sync_strategy=outbound_payload.sync_strategy,
            field_mappings=TypeAdapter(StoredMappingValue).validate_python(outbound_payload.field_mappings),
            current_form_parameters={},
        )
        outbound_sync_request = OutboundSyncRequest(
            run_id=outbound_payload.run_id,
            session=self.session,
            source_app_name=self.omnata_app_name,
            results_schema_name=outbound_payload.results_schema_name,
            results_table_name=outbound_payload.results_table_name,
            records_schema_name=outbound_payload.records_schema_name,
            records_table_name=outbound_payload.records_table_name,
            plugin_instance=self.plugin_instance,
            api_limits=self.api_limits,
            rate_limit_state_all={},
            rate_limit_state_this_sync_and_branch={},
            run_deadline=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4),
            development_mode=True,
        )

        self.current_scenario = SyncScenario(
            plugin_id=self.plugin_id,
            scenario_name=scenario_name,
            configuration_parameters=configuration_parameters,
            sync_direction=SyncDirection.OUTBOUND,
            sync_request=outbound_sync_request,
            scenario_records=scenario_records,
        )
        self.run_id = outbound_payload.run_id
        outbound_sync_request._prebaked_record_state = scenario_records
        self.plugin_instance._sync_request = outbound_sync_request
        if self.recorded_http:
            self._start_recording()
        return configuration_parameters, outbound_sync_request

    def prepare_inbound_scenario_from_sync(
        self,
        scenario_name: str,
        sync_slug: str,
        current_stream_state: Dict = None,
        snowcli_environment: str = "dev",
    ) -> Tuple[InboundSyncConfigurationParameters, InboundSyncRequest]:
        """
        Prepares an outbound sync scenario using a Sync which has been fully configured in the Omnata app.
        The user must have the Omnata application role PLUGIN_DEVELOPER, as well as having develop privileges
        on the plugin app.
        Optionally, the current stream state can be provided, which will be used to set the initial state of the streams
        """
        # first, check to see if there's no click context, happens in Jupyter notebooks
        if not click.globals.get_current_context(silent=True):
            # set an empty one so snowcli's app config doesn't error
            click.globals.push_context(click.core.Context(click.core.Group()))
        
        self.session: Session = get_snowpark_session(connection_name=snowcli_environment)
        # we set the current database to the plugin app name, if it's set in the environment
        # this means any plugins which call their own UDFs will work
        if 'PLUGIN_APP_NAME' in os.environ:
            plugin_app_name = os.environ['PLUGIN_APP_NAME']
            self.session.sql(f"USE DATABASE {plugin_app_name}").collect()

        self.sync_slug = sync_slug
        session_run_response = self.session.sql(
            f"""
            call {self.omnata_app_name}.API.CREATE_DEVELOPMENT_SESSION_RUN('{sync_slug}')
            """
        ).collect()
        response_parsed = json.loads(session_run_response[0][0])
        if response_parsed["success"] is False:
            raise ValueError(f"Failed: {response_parsed['error']}")
        response_data = response_parsed["data"]
        if "direction" not in response_data:
            raise ValueError(
                f"Invalid response from CREATE_DEVELOPMENT_SESSION_RUN: {response_data}"
            )
        if response_data["direction"] != "inbound":
            raise ValueError("The provided sync is not an inbound sync")
        if "inbound_apply_payload" not in response_data:
            raise ValueError(
                f"Invalid response from CREATE_DEVELOPMENT_SESSION_RUN: {response_data}"
            )
        if "plugin_app_name" not in response_data:
            raise ValueError(
                f"Invalid response from CREATE_DEVELOPMENT_SESSION_RUN: {response_data}"
            )
        plugin_app_name = response_data["plugin_app_name"]
        inbound_payload = InboundSyncRequestPayload.model_validate(
            response_data["inbound_apply_payload"]
        )

        # we have everything we need except the secrets, which we fetch from the plugin app
        oauth_secret_param = (
            f"'{inbound_payload.oauth_secret_name}'"
            if inbound_payload.oauth_secret_name
            else "null"
        )
        other_secrets_param = (
            f"'{inbound_payload.other_secrets_name}'"
            if inbound_payload.other_secrets_name
            else "null"
        )

        secrets_fetch_response = self.session.sql(
            f"""
            call {plugin_app_name}.PLUGIN.RETRIEVE_SECRETS({oauth_secret_param},{other_secrets_param})
            """
        ).collect()
        secrets_response_parsed = json.loads(secrets_fetch_response[0][0])
        if secrets_response_parsed["success"] is False:
            raise ValueError(f"Failed: {secrets_response_parsed['error']}")
        secrets_data = TypeAdapter(
            Dict[str, StoredConfigurationValue]).validate_python(secrets_response_parsed["data"])

        # full_source_table_name = f"{source_database}.{source_schema}.{source_table}"
        # self.api_limits.concurrency = 1 # we have to set this because pyvcr isn't thread safe
        configuration_parameters = InboundSyncConfigurationParameters(
            connection_method=inbound_payload.connection_method,
            connection_parameters=TypeAdapter(
                Dict[str, StoredConfigurationValue]).validate_python(
                inbound_payload.connection_parameters,
            ),
            connection_secrets=TypeAdapter(
                Dict[str, StoredConfigurationValue]).validate_python(secrets_data
            ),
            sync_parameters=TypeAdapter(
                Dict[str, StoredConfigurationValue]).validate_python(inbound_payload.sync_parameters
            ),
            current_form_parameters={},
        )

        streams_list = list(
            inbound_payload.streams_configuration.included_streams.values()
        )
        initial_stream_state = (
            copy.deepcopy(inbound_payload.latest_stream_state)
            if current_stream_state is None
            else current_stream_state
        )
        for stream in streams_list:
            if stream.stream.source_defined_primary_key is not None:
                self.stream_index_fields[stream.stream_name] = stream.stream.source_defined_primary_key
        omnata_log_handler = OmnataPluginLogHandler(
            session=self.session,
            sync_id=None,
            sync_branch_id=None,
            connection_id=None,
            sync_run_id=inbound_payload.run_id,
        )
        inbound_sync_request = InboundSyncRequest(
            run_id=inbound_payload.run_id,
            session=self.session,
            source_app_name=self.omnata_app_name,
            results_schema_name=inbound_payload.results_schema_name,
            results_table_name=inbound_payload.results_table_name,
            plugin_instance=self.plugin_instance,
            api_limits=self.api_limits,
            rate_limit_state_all={},
            rate_limit_state_this_sync_and_branch={},
            run_deadline=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4),
            development_mode=True,
            # this skips over the part where we check for new streams etc,
            # so development sessions will only get requests for explicitly configured streams
            streams=streams_list,
            omnata_log_handler=omnata_log_handler
        )

        self.current_scenario = SyncScenario(
            plugin_id=self.plugin_id,
            scenario_name=scenario_name,
            sync_direction=SyncDirection.INBOUND,
            configuration_parameters=configuration_parameters,
            sync_request=inbound_sync_request,
            scenario_records=None,
            initial_stream_state=initial_stream_state
        )
        self.run_id = inbound_payload.run_id
        self.plugin_instance._sync_request = inbound_sync_request
        if self.recorded_http:
            self._start_recording()
        return configuration_parameters, inbound_sync_request
    
    def cancel_scenario(self):
        """
        Cancels the current scenario, and stops recording traffic.
        """
        if self.current_scenario is None:
            return "Failed: you need to call prepare_outbound_scenario or prepare_inbound_scenario first"
        self.current_scenario = None
        if self.recorded_http:
            self._stop_recording()
        print("Success: cancelled scenario")

    def complete_scenario(self,apply_results:bool=True):
        """
        Marks the scenario as complete, and stops recording traffic.
        """
        if self.current_scenario is None:
            return "Failed: you need to call prepare_outbound_scenario or prepare_inbound_scenario first"
        if self.current_scenario.results is None and apply_results:
            return "Failed: you need to pass the results back to validate_response() before completing the scenario"
        self.recorded_scenarios.append(self.current_scenario)
        if self.recorded_http:
            self._stop_recording()
        if apply_results:
            self.current_scenario.sync_request.apply_results_queue()
            if self.current_scenario.sync_request.__class__.__name__ == "InboundSyncRequest":
                print(f'States at completion: {self.current_scenario.sync_request._latest_states}')
                self.current_scenario.sync_request.apply_progress_updates(ignore_errors=False)
        session_run_response = self.session.sql(
            f"""
            call {self.omnata_app_name}.API.COMPLETE_DEVELOPMENT_SESSION_RUN({self.run_id},{apply_results})
            """
        ).collect()
        response_parsed = json.loads(session_run_response[0][0])
        if response_parsed["success"] is False:
            raise ValueError(f"Failed: {response_parsed['error']}")
        self.current_scenario = None
        print("Success: finished recording scenario")

    def _stop_recording(self):
        """
        Stops the pyvcr recording
        """
        self.vcr.__exit__()

    def _start_recording(self):
        """
        Configures and starts the pyvcr recording
        """
        my_vcr = vcr.VCR(
            before_record_request=scrub_secrets(
                self.current_scenario.configuration_parameters.connection_secrets
            ),
            record_mode="all",
            decode_compressed_response=True,
            filter_query_parameters=self.vcr_filter_query_parameters,
            filter_headers=[
                ("authorization", "[redacted]"),
                ("x-api-key", "[redacted]"),
            ],
        )
        self.cassette_filename = self.current_scenario.scenario_cassette_file
        if os.path.exists(self.cassette_filename):
            os.remove(self.cassette_filename)
        self.vcr = my_vcr.use_cassette(self.cassette_filename)
        self.vcr.__enter__()  # pylint: disable=unnecessary-dunder-call  # Multiple steps span the context manager boundary

    def _restart_recording(self):
        """
        Stops and starts the recording
        """
        self._stop_recording()
        self._start_recording()

    def validate_response(self, sync_request: SyncRequest) -> str:
        """
        Tests that the response to a record apply request is valid. This will check that the DataFrame
        has all of the correct columns, and that results of all the originally requested records are included
        """
        if sync_request.__class__.__name__ == "OutboundSyncRequest":
            outbound_sync_request: OutboundSyncRequest = sync_request
            if (
                outbound_sync_request._apply_results is None
                or len(outbound_sync_request._apply_results) == 0
            ):
                print("Failed: No results were enqueued to the sync request")
                return
            if self.current_scenario is None:
                print("Failed: no active scenario")
                return
            results_dataframe = pandas.concat(outbound_sync_request._apply_results).copy()

            originally_provided_records = self.current_scenario.scenario_records

            if originally_provided_records is None:
                print("Failed: cannot locate originally provided values")
                return
            column_list = list(results_dataframe.columns)
            if "IDENTIFIER" not in column_list:
                print('Failed: "IDENTIFIER" column not in dataframe')
                return
            if "APP_IDENTIFIER" in column_list:
                if not pandas.api.types.is_string_dtype(
                    results_dataframe["APP_IDENTIFIER"]
                ):
                    print(
                        'Failed: "APP_IDENTIFIER" column is not a string type. Use ".astype(str)" to enforce string conversion'
                    )
                    return

            if "SUCCESS" not in column_list:
                print('Failed: "SUCCESS" column not in dataframe')
                return
            if not pandas.api.types.is_bool_dtype(results_dataframe["SUCCESS"]):
                print('Failed: "SUCCESS" column is not a boolean type')
                return
            if "RESULT" not in column_list:
                print('Failed: "RESULT" column not in dataframe')
                return
            if not results_dataframe["RESULT"].dtype == "O":
                return f"Failed: \"RESULT\" column should contain objects, instead the data type is {results_dataframe['RESULT'].dtype}"
            # merge results back on to original, so we can find the missing identifiers
            merged_results = pandas.merge(
                left=originally_provided_records[["IDENTIFIER"]],
                right=results_dataframe,
                left_on="IDENTIFIER",
                right_on="IDENTIFIER",
                how="left",
            )
            missing_in_results = merged_results["SUCCESS"].isna()
            if missing_in_results.sum() > 0:
                missing_identifiers = merged_results[missing_in_results]["IDENTIFIER"]
                print(
                    f"Warning: Missing results for {missing_in_results.sum()} records from apply request: {list(missing_identifiers)}"
                )
            self.current_scenario.results = results_dataframe
            print("Success: results are valid")
        elif sync_request.__class__.__name__ == "InboundSyncRequest":
            inbound_sync_request: InboundSyncRequest = sync_request
            if inbound_sync_request._apply_results is None or len(inbound_sync_request._apply_results) == 0:
                # if there are no results, we check the real results table
                full_table_name = inbound_sync_request._full_results_table_name
                # usually if results are provided in a table, RECORD_OBJECT (object) is used instead of RECORD_DATA (varchar)
                # note that it will still be JSON in the dataframe as that's how the snowflake connector returns it
                results_from_table = self.session.sql(f"""
                    select APP_IDENTIFIER,
                        STREAM_NAME,
                        RETRIEVE_DATE,
                        COALESCE(PARSE_JSON(RECORD_DATA), RECORD_OBJECT) as RECORD_OBJECT,
                        IS_DELETED
                    from {full_table_name}""").collect()
                
                if len(results_from_table) == 0:
                    print(f"Failed: No results were enqueued to the sync request, and no results found in {full_table_name}")
                else:
                    results_dataframe = pandas.DataFrame(results_from_table)
                    results_dataframe["RECORD_OBJECT"] = results_dataframe["RECORD_OBJECT"].apply(
                        lambda x: json.loads(x) if x is not None else None
                    )
                    self.current_scenario.results = results_dataframe
                    print("Success: results are valid (retrieved from table)")
            else:
                # inbound_sync_request._apply_results is a dictionary of stream_name -> list of dataframes
                # we want to flatten this into a single dataframe
                results_dataframe = pandas.concat(
                    [df for df_list in inbound_sync_request._apply_results.values() for df in df_list]
                ).copy()
                # typically, the results table will have a RECORD_DATA column, which is a varchar
                # we need to parse this as JSON into an object column named RECORD_OBJECT, allowing for nulls
                results_dataframe["RECORD_OBJECT"] = results_dataframe["RECORD_DATA"].apply(
                    lambda x: json.loads(x) if x is not None else None
                )
                # we can drop the RECORD_DATA column now
                results_dataframe = results_dataframe.drop(columns=["RECORD_DATA"])
                self.current_scenario.results = results_dataframe
                print("Success: results are valid")
        else:
            raise ValueError(
                f"Failed: sync request is not an OutboundSyncRequest or InboundSyncRequest, it is a {sync_request.__class__.__name__}"
            )

    def dataframe_to_behave_table(
        self,
        data_frame: pandas.DataFrame,
        indent_tabs: int,
        include_data_type: bool = True,
    ):
        """
        Converts a pandas DataFrame into a formatted Behave table
        """
        tabulated_df = tabulate(
            data_frame,
            headers="keys",
            tablefmt="pipe",
            showindex=False,
            disable_numparse=True,
        )
        # break the string representation of the table into rows so that we can tweak it a bit
        table_lines = re.split("(?<![\\\\])\\n", tabulated_df)
        # remove the line that tabulate puts between heading and values, behave doesn't like it
        del table_lines[1]
        # insert a line at the top for the data type
        top_heading = table_lines[0]
        if include_data_type:
            for df_col in data_frame.columns:
                # just use strings for everything except SUCCESS and RESULT
                if df_col == "SUCCESS":
                    dtype = "bool"
                elif df_col == "RESULT":
                    dtype = "object"
                else:
                    dtype = "str"  # str(df[col].dtype)
                top_heading = top_heading.replace(
                    f" {df_col} ", " " + dtype.ljust(len(df_col) + 1, " ")
                )
            table_lines.insert(0, top_heading)
        tabs = indent_tabs * "\t"
        table_lines_indented = [f"{tabs}{line}" for line in table_lines]
        table_indented = "\n".join(table_lines_indented)
        return table_indented

    def generate_behave_test(self):
        """
        Generates a Python Behave test, following completed test scenarios
        """
        if len(self.recorded_scenarios) == 0:
            print(
                "Failed: No recorded scenarios found - did you forget to call complete_scenario()?"
            )
            return
        if self.current_scenario is not None:
            print(
                "Warning: there is scenario currently running, please call complete_scenario() if you want it included"
            )

        f = open(self.feature_filename, "w", encoding="utf-8")
        print(f"Writing feature file: {self.feature_filename}\n")
        f.write(f"Feature: Apply records for the {self.sync_slug} sync\n")
        for recorded_scenario in self.recorded_scenarios:
            # strip unescaped newlines from json string
            secrets_redacted = {}
            for (
                secret_name,
                value,
            ) in recorded_scenario.configuration_parameters.connection_secrets.items():
                if not self.recorded_http:
                    if "{{environ['" not in value.value:
                        raise ValueError(
                            f"Scenario {recorded_scenario.scenario_name} does not use recorded HTTP and contains a secret value '{secret_name}' which has not been replaced with an environment variable"
                        )
                else:
                    if isinstance(value, StoredConfigurationValue):
                        value.value = "[redacted]"
                    else:
                        raise ValueError(
                            f"Secret {secret_name} does not contain a StoredConfigurationValue"
                        )
                secrets_redacted[secret_name] = value.model_dump()
            if isinstance(
                recorded_scenario.configuration_parameters,
                OutboundSyncConfigurationParameters,
            ):
                outbound_params: OutboundSyncConfigurationParameters = (
                    recorded_scenario.configuration_parameters
                )
                properties_df = pandas.DataFrame(
                    [
                        {
                            "Property": "strategy",
                            "Value": json.dumps(
                                outbound_params.sync_strategy.model_dump()
                            ),
                        },
                        {
                            "Property": "connection_method",
                            "Value": recorded_scenario.configuration_parameters.connection_method,
                        },
                        {
                            "Property": "connection_parameters",
                            "Value": json.dumps(
                                to_jsonable_python(outbound_params.connection_parameters)
                            ),
                        },
                        {
                            "Property": "connection_secrets",
                            "Value": json.dumps(
                                to_jsonable_python(secrets_redacted)
                            ),
                        },
                        {
                            "Property": "api_limits",
                            "Value": json.dumps(
                                to_jsonable_python(self.api_limits)
                            ),
                        },
                        {
                            "Property": "sync_parameters",
                            "Value": json.dumps(
                                to_jsonable_python(outbound_params.sync_parameters)
                            ).replace("|", "\\|"),
                        },
                        {
                            "Property": "field_mappings",
                            "Value": json.dumps(
                                to_jsonable_python(outbound_params.field_mappings)
                            ).replace("|", "\\|"),
                        },
                    ]
                )
            else:
                inbound_params: InboundSyncConfigurationParameters = (
                    recorded_scenario.configuration_parameters
                )
                inbound_sync_request: InboundSyncRequest = (
                    recorded_scenario.sync_request
                )
                properties_df = pandas.DataFrame(
                    [
                        {
                            "Property": "connection_method",
                            "Value": recorded_scenario.configuration_parameters.connection_method,
                        },
                        {
                            "Property": "connection_parameters",
                            "Value": json.dumps(
                                to_jsonable_python(inbound_params.connection_parameters)
                            ),
                        },
                        {
                            "Property": "connection_secrets",
                            "Value": json.dumps(
                                to_jsonable_python(secrets_redacted)
                            ),
                        },
                        {
                            "Property": "api_limits",
                            "Value": json.dumps(
                                to_jsonable_python(self.api_limits)
                            ),
                        },
                        {
                            "Property": "sync_parameters",
                            "Value": json.dumps(
                                to_jsonable_python(inbound_params.sync_parameters)
                            ).replace("|", "\\|"),
                        },
                        {
                            "Property": "streams",
                            "Value": json.dumps(
                                to_jsonable_python(inbound_sync_request.streams)
                            ),
                        },
                    ]
                )
            print(
                f"Writing scenario: {recorded_scenario.scenario_name} cassette: {recorded_scenario.scenario_cassette_file_name}\n"
            )
            f.write(f"\tScenario: {recorded_scenario.scenario_name}\n")
            if recorded_scenario.sync_direction == SyncDirection.OUTBOUND:
                f.write("\t\tGiven the following records:\n")
                for col in ["RESULT","TRANSFORMED_RECORD", "TRANSFORMED_RECORD_PREVIOUS"]:
                    recorded_scenario.scenario_records[col] = (
                        recorded_scenario.scenario_records[col]
                        .apply(lambda x: json.loads(x) if x is not None else None)
                        .apply(json.dumps, separators=(",", ":"))
                    )
                    recorded_scenario.scenario_records[col] = (
                        recorded_scenario.scenario_records[col]
                        .str.replace("(?<![\\\\])\\n", "")
                        .str.replace("|", "\\|")
                    )
                table_indented = self.dataframe_to_behave_table(
                    recorded_scenario.scenario_records[
                        ["IDENTIFIER", "APP_IDENTIFIER", "RESULT", "SYNC_ACTION", "TRANSFORMED_RECORD","TRANSFORMED_RECORD_PREVIOUS"]
                    ],
                    3,
                )
                f.write(f"{table_indented}\n")
            else:
                f.write("\t\tGiven the following streams state:\n")
                f.write("\t\t\t| Stream | Value | \n")
                inbound_sync_request: InboundSyncRequest = (
                    recorded_scenario.sync_request
                )
                for stream in inbound_sync_request.streams:
                    if recorded_scenario.initial_stream_state is not None and stream.stream_name in recorded_scenario.initial_stream_state:
                        f.write(
                            f"\t\t\t| {stream.stream_name} | {json.dumps(recorded_scenario.initial_stream_state[stream.stream_name],separators=(',', ':'),default=str)} | \n"
                        )
                    else:
                        f.write(f"\t\t\t| {stream.stream_name} | {{}} | \n")
            if len(self.vcr_filter_query_parameters) > 0:
                f.write(
                    f"\t\tAnd when matching requests, we ignore query parameters {','.join(self.vcr_filter_query_parameters)}\n"
                )
            if self.recorded_http:
                f.write(
                    f"\t\tAnd we use the HTTP recordings from {recorded_scenario.scenario_cassette_file_name}\n"
                )
            table_indented = self.dataframe_to_behave_table(
                properties_df, 3, include_data_type=False
            )
            f.write(
                f"\t\tAnd we use the {self.plugin_instance.__class__.__name__} class from the {self.plugin_module} module\n"
            )
            if self.inject_snowpark_session:
                f.write(
                    f"\t\tAnd we attach a Snowpark session to the sync request\n"
                )
                f.write(
                    f"\t\tAnd the plugin returns inbound sync results directly to a real table\n"
                )
            if recorded_scenario.sync_direction == SyncDirection.OUTBOUND:
                f.write(
                    "\t\tWhen we perform an outbound sync with configuration parameters:\n"
                )
            else:
                f.write(
                    "\t\tWhen we perform an inbound sync with configuration parameters:\n"
                )
            f.write(f"{table_indented}\n")
            f.write(f"\t\tAnd we use the recorded results from {recorded_scenario.inbound_results_file_name}\n")
            if recorded_scenario.sync_direction == SyncDirection.OUTBOUND:
                f.write("\t\tAnd the response will be:\n")
                # self.create_results['TRANSFORMED_RECORD']=self.create_results['TRANSFORMED_RECORD'].apply(json.dumps)
                recorded_scenario.results["RESULT"] = recorded_scenario.results[
                    "RESULT"
                ].apply(json.dumps)
                recorded_scenario.results.loc[
                    recorded_scenario.results["RESULT"] == '"null"', "RESULT"
                ] = "null"
                recorded_scenario.results = recorded_scenario.results[
                    recorded_scenario.results.columns.intersection(
                        ["IDENTIFIER", "SUCCESS", "APP_IDENTIFIER", "RESULT"]
                    )
                ]
                table_indented = self.dataframe_to_behave_table(
                    recorded_scenario.results, 3
                )
                f.write(f"{table_indented}\n")
            else:
                # write the results from self.current_scenario.results out to a csv file, pipe delimited
                # the file name is stored at self.inbound_results_file
                # before we write it out, we need to remove any excluded fields, using self.stream_excluded_fields
                # The fields are inside the RECORD_OBJECT object column
                for stream_name in recorded_scenario.results["STREAM_NAME"].unique():
                    if stream_name in self.stream_excluded_fields:
                        excluded_fields = self.stream_excluded_fields[stream_name]
                        recorded_scenario.results.loc[
                            recorded_scenario.results["STREAM_NAME"] == stream_name,
                            "RECORD_OBJECT",
                        ] = recorded_scenario.results.loc[
                            recorded_scenario.results["STREAM_NAME"] == stream_name,
                            "RECORD_OBJECT",
                        ].apply(
                            lambda x: {
                                k: v
                                for k, v in x.items()
                                if k not in excluded_fields
                            }
                        )
                        f.write(
                            f"\t\tAnd we exclude the following fields from the inbound results for the {stream_name} stream: {','.join(excluded_fields)}\n"
                        )
                # any records excluded by field value are removed both in the recording and the test
                if len(self.exclude_records_by_field_value) > 0:
                    for field_name, field_value in self.exclude_records_by_field_value.items():
                        if field_value == 'true':
                            field_value = True
                        elif field_value == 'false':
                            field_value = False
                        recorded_scenario.results["value_test"] = recorded_scenario.results["RECORD_OBJECT"].apply(
                            lambda x: x[field_name] if x is not None and field_name in x else None
                        )
                        matching_records = recorded_scenario.results[recorded_scenario.results["value_test"] == field_value]
                        print(f"Excluded {len(matching_records)} records where {field_name} is {field_value}")
                        recorded_scenario.results = recorded_scenario.results[recorded_scenario.results["value_test"] != field_value]
                        # remove the temporary column
                        recorded_scenario.results.drop(columns=["value_test"],inplace=True)


                # convert the RECORD_OBJECT to a json string without newlines
                recorded_scenario.results["RECORD_OBJECT"] = recorded_scenario.results[
                    "RECORD_OBJECT"
                ].apply(json.dumps)
                # also, drop the RETRIEVE_DATE column
                recorded_scenario.results.drop(columns=["RETRIEVE_DATE"],inplace=True)
                # create the results file if it doesn't exist
                os.makedirs(os.path.dirname(recorded_scenario.inbound_results_file), exist_ok=True)
                recorded_scenario.results.to_csv(recorded_scenario.inbound_results_file, sep="|", index=False)

                if len(self.exclude_records_by_field_value) > 0:
                    for field_name, field_value in self.exclude_records_by_field_value.items():
                        f.write(f"\t\tAnd we exclude all inbound results where the field {field_name} has the value {field_value}\n")
                # group the results by stream name
                stream_names = recorded_scenario.results["STREAM_NAME"].unique()

                for stream_name in stream_names:
                    if stream_name not in self.stream_index_fields:
                        print(f"Failed: no index field set for stream {stream_name}. Use the set_inbound_stream_index_field function to set one")
                        return
                    f.write(
                        f"\t\tAnd when indexed on the {self.stream_index_fields[stream_name]} RECORD_OBJECT field, we assert that the recorded results for the {stream_name} stream are correct\n"
                    )
                    # count the number of records in the results that have a STREAM_NAME of stream_name
                    stream_results = recorded_scenario.results[recorded_scenario.results["STREAM_NAME"] == stream_name]
                    if len(stream_results) == 0:
                        raise ValueError(f"Recorded results for scenario {recorded_scenario.scenario_name} did not contain any results for stream {stream_name}")
                    #results = pandas.concat(recorded_scenario.results[stream_name])
                    ## no need to do this anymore, as the results are already json
                    ##results["RECORD_DATA"] = results["RECORD_DATA"].apply(json.dumps)
                    #results["RECORD_DATA"] = results["RECORD_DATA"].replace("|", "\\|")
                    #results.loc[
                    #    results["RECORD_DATA"] == '"null"', "RECORD_DATA"
                    #] = "null"
                    #results = results[
                    #    results.columns.intersection(
                    #        [
                    #            "APP_IDENTIFIER",
                    #            "RECORD_DATA",
                    #            "RETRIEVE_DATE",
                    #            "STREAM_NAME",
                    #        ]
                    #    )
                    #]
                    #table_indented = self.dataframe_to_behave_table(results, 3)
                    #f.write(f"{table_indented}\n")

        f.close()
        print("Finished writing feature file")
        steps_importer_file = os.path.join("features", "steps", "imported_steps.py")
        os.makedirs(os.path.dirname(steps_importer_file), exist_ok=True)
        print(f"Writing steps importer file: {steps_importer_file}\n")
        with open(steps_importer_file, "w") as f:
            f.write("import omnata_plugin_devkit.test_step_definitions")
        print(f"Success: wrote out all test-related files\n")
        print(
            f'You can now run the tests by installing the "behave" package and running "behave features" from the root of your plugin ("!behave features" from within a Jupyter cell)\n'
        )

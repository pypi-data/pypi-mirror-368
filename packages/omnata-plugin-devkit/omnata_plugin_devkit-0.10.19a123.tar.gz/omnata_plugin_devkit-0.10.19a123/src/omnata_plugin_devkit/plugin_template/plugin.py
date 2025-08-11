"""
This module contains the implementation of the Omnata Plugin for TemplateApp.
"""
from omnata_plugin_runtime.forms import (
    InboundSyncConfigurationForm,
    OutboundSyncConfigurationForm,
    DynamicFormOptionsDataSource,
    FormFieldMappingSelector,
    ConnectionMethod,
    FormInputField,
    FormOption,
    StaticFormOptionsDataSource,
    FormDropdownField,
    FormSshKeypair,
    FormTextAreaField,
    FormCheckboxField,
    NewOptionCreator,
)
from omnata_plugin_runtime.omnata_plugin import (
    InboundSyncRequest,
    OmnataPlugin,
    PluginManifest,
    ConnectResponse,
    OutboundSyncRequest,
    managed_outbound_processing,
)
from omnata_plugin_runtime.configuration import (
    CreateSyncStrategy,
    UpdateSyncStrategy,
    OutboundSyncConfigurationParameters,
    ConnectionConfigurationParameters,
    InboundSyncConfigurationParameters,
    OutboundSyncStrategy,
    OutboundSyncAction,
    CreateSyncAction,
    UpdateSyncAction,
    DeleteSyncAction,
    StreamConfiguration,
    StoredStreamConfiguration,
    InboundStorageBehaviour,
    InboundSyncStrategy
)
from typing import List
import logging
import requests
import pandas
import json

logger = logging.getLogger("omnata_plugin")


class TemplateApp(OmnataPlugin):
    """
    Omnata Plugin for TemplateApp
    """

    def __init__(self):
        """
        The plugin class for TemplateApp
        """
        OmnataPlugin.__init__(self)

    def get_manifest(self) -> PluginManifest:
        return PluginManifest(
            plugin_id="template_app",
            plugin_name="TemplateApp",
            developer_id="my_company",
            developer_name="My Company",
            docs_url="https://docs.mycompany.com",
            supports_inbound=True,
            supported_outbound_strategies=[CreateSyncStrategy(), UpdateSyncStrategy()],
        )

    def connection_form(self) -> List[ConnectionMethod]:
        """
        Returns one or more ConnectionMethod objects, each of which define a form for
        the user to complete during the connection process.
        """
        return [
            ConnectionMethod(
                name="API Key",
                fields=[
                    FormInputField(
                        name="api_key", label="API Key", required=True, secret=True
                    )
                ],
            )
        ]

    def network_addresses(
        self, parameters: ConnectionConfigurationParameters
    ) -> List[str]:
        # Addresses specified here will be permitted for access before connect() is called
        return ["login.template-app.com"]

    def connect(self, parameters: ConnectionConfigurationParameters) -> ConnectResponse:
        """
        Takes the parameters that the user entered in the connection form and tests the connection.
        Alternatively, the ConnectResponse can contain OAuth parameters which will initiate an OAuth flow.
        """
        # call the login url with the API key in the header
        api_key = parameters.connection_secrets.get("api_key").value
        response = requests.get(
            url="https://login.template-app.com",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60,
        )
        if response.status_code != 200:
            raise ValueError(f"Connection failed: {response.status_code}")
        tenant_url = response.json()["tenant_url"]
        return ConnectResponse(
            # anything which is useful to store with the Connection can be provided here
            connection_parameters={"tenant_url", tenant_url},
            # addresses specified here will be permitted before configuration form methods are called
            network_addresses=[tenant_url],
        )

    def outbound_configuration_form(
        self, parameters: OutboundSyncConfigurationParameters
    ) -> OutboundSyncConfigurationForm:
        """
        Generates a configuration form which gathers the information needed to sync data out of Snowflake.
        """
        return OutboundSyncConfigurationForm(
            fields=[
                FormDropdownField(
                    name="target_object",
                    label="Target Object",
                    help_text="The object to sync data into",
                    # this provides a fixed set of options in the UI
                    data_source=StaticFormOptionsDataSource(
                        values=[
                            FormOption(label="Lead", value="Lead"),
                            FormOption(label="Contact", value="Contact"),
                            FormOption(label="Account", value="Account"),
                        ]
                    ),
                ),
            ],
            mapper=FormFieldMappingSelector(
                depends_on="target_object",
                # this will be populated dynamically after the target object is selected
                data_source=DynamicFormOptionsDataSource(
                    source_function=self.field_mappings
                ),
            ),
        )

    def field_mappings(self, parameters: OutboundSyncConfigurationParameters) -> List[FormOption]:
        """
        This is a handler which populates the field mapping options based on the target object selected.
        Each FormOption returned here will be available as a field mapping target in the UI.
        """
        target_object = parameters.get_sync_parameter("target_object").value
        tenant_url = parameters.get_connection_parameter("tenant_url").value
        # fetch a list of fields for the chosen target object
        fields_response = requests.get(
            url=f"{tenant_url}/api/v1/fields/{target_object}", timeout=60
        )
        if fields_response.status_code != 200:
            raise ValueError(f"Failed to fetch fields: {fields_response.status_code}")
        fields = fields_response.json()
        fields_to_return = []
        for field in fields["fields"]:
            # don't include fields that can't be populated
            fields_to_return.append(
                FormOption(
                    value=field["name"],
                    label=field["label"],
                    required=field["mandatory"],
                    unique=field["unique"],
                    metadata=field,
                )
            )

        return sorted(fields_to_return, key=lambda d: d.label)

    def sync_outbound(
        self,
        parameters: OutboundSyncConfigurationParameters,
        outbound_sync_request: OutboundSyncRequest,
    ):
        """
        Applies a set of changed records to an app. This function is called whenever a run occurs and changed records
        are found.
        To return results, either:
        - return one big dataframe at the end
        - invoke outbound_sync_request.enqueue_results() during the load process
        - return a dataframe from a managed_outbound_processing() function

        :param PluginConfigurationParameters parameters the parameters of the sync, as configured by the user
        :param OutboundSyncRequest outbound_sync_request an object describing what has changed
        :return None
        :raises ValueError: if issues were encountered during connection
        """
        target_object = parameters.get_sync_parameter("target_object").value
        tenant_url = parameters.get_connection_parameter("tenant_url").value
        # If you don't need the fixed sized batching/parallelization features of the plugin runtime, you can
        # just iterate over the records and process them one by one, like so:
        if parameters.sync_strategy.name == CreateSyncStrategy.name:
            # create new records
            for record in outbound_sync_request.get_records(sync_actions=[CreateSyncAction()]):
                # create the record
                response = requests.post(
                    url=f"{tenant_url}/api/v1/{target_object}", json=record, timeout=60
                )
                if response.status_code != 200:
                    raise ValueError(f"Failed to create record: {response.status_code}")
                # get the ID of the newly created record
                record_id = response.json()["id"]
                # add the ID to the record so that it can be updated later
                record["id"] = record_id
                # enqueue the record to be returned to Omnata
                outbound_sync_request.enqueue_results([record])
        # Alternatively, you can pass the dataframe generator off to a managed_outbound_processing function
        # and it will automatically invoke the function in parallel with fixed sized batches
        self.create_records(
            outbound_sync_request.get_records(batched=True, sync_actions=[CreateSyncAction()]),
            target_object=target_object,
            tenant_url=tenant_url,
        )
        # then update records, you get the idea..
        # self.update_records(outbound_sync_request.get_records(batched=True,sync_actions=[UpdateSyncAction()]),
        #                    target_object=target_object,
        #                    tenant_url=tenant_url)

    # splits input dataframe into batches with no more than 100 records each,
    # invoked in parallel with a maximum of 2 concurrent calls
    @managed_outbound_processing(concurrency=2, batch_size=100)
    def create_records(
        self, data_frame: pandas.DataFrame, target_object: str, tenant_url: str
    ) -> pandas.DataFrame:
        """
        This function is called in parallel with fixed sized batches of records.
        This makes it simpler to work with APIs which have mini-bulk endpoints (e.g. 100 records at a time).
        """
        # collapse the 100 records into a single json array, with 'records' as the root field
        records_array_json = data_frame["TRANSFORMED_RECORD"].to_json(orient="records")
        records_array = json.loads(records_array_json)
        response = requests.post(
            url=f"{tenant_url}/api/v1/{target_object}/create",
            json=records_array,
            timeout=60,
        )
        if response.status_code != 200:
            # Throwing an exception will automatically fail all the records in the batch
            raise ValueError(f"Failed to create records: {response.status_code}")
        
        # since the HTTP request worked, now we have to return a dataframe containing the outcome of each record
        results_frame = pandas.DataFrame(response["results"])
        # response contains results in same order, so merge back on index. Alternatively, if the API returned results
        # keyed on the IDENTIFIER column from the input dataframe, you could merge on that column instead.
        data_frame = pandas.merge(
            data_frame, results_frame, left_index=True, right_index=True
        )
        # assign an App Identifier to the records
        data_frame["APP_IDENTIFIER"] = data_frame["id"].astype(str)
        # set the success flag based on the presence of errors
        data_frame = data_frame.assign(
            SUCCESS=lambda x: "error" not in x or x["error"] == ""
        )
        # set any other useful information from the app
        data_frame["RESULT"] = data_frame["details"]
        # pass back the original identifiers, mapped to the information gathered above
        return data_frame[["IDENTIFIER", "SUCCESS", "APP_IDENTIFIER", "RESULT"]]

    def inbound_configuration_form(
        self, parameters: InboundSyncConfigurationParameters
    ) -> InboundSyncConfigurationForm:
        """
        Generates a configuration form which gathers the information needed to sync data in to Snowflake.
        """
        # This works much the same way as the outbound configuration form, but is used for inbound syncs
        # and doesn't have a mapper field
        return InboundSyncConfigurationForm(
            fields=[
            ]
        )

    def inbound_stream_list(
        self, parameters: InboundSyncConfigurationParameters
    ) -> List[StreamConfiguration]:
        """
        This method is invoked after the user has configured the inbound sync, and returns a list of streams
        that the user can choose from to sync data from. Any configuration parameters from the form above
        can be accessed via the parameters object.
        """
        tenant_url = parameters.get_connection_parameter("tenant_url").value
        streams = []
        streams.append(
            StreamConfiguration(
                stream_name="leads",
                supported_sync_strategies=[InboundSyncStrategy.FULL_REFRESH, InboundSyncStrategy.INCREMENTAL]
            ),
            StreamConfiguration(
                stream_name="contacts",
                supported_sync_strategies=[InboundSyncStrategy.FULL_REFRESH, InboundSyncStrategy.INCREMENTAL]
            ),
        )
        response = requests.get(
            url=f"{tenant_url}/api/v1/custom_objects",
            timeout=60,
        )
        if response.status_code != 200:
            raise ValueError(f"Failed to list custom objects: {response.status_code}")
        custom_objects = response.json()
        for custom_object in custom_objects:
            streams.append(
                StreamConfiguration(
                    stream_name=custom_object["name"],
                    supported_sync_strategies=[InboundSyncStrategy.FULL_REFRESH, InboundSyncStrategy.INCREMENTAL]
                )
            )

    def sync_inbound(
        self,
        parameters: InboundSyncConfigurationParameters,
        inbound_sync_request: InboundSyncRequest,
    ):
        """
        Retrieves the next set of records from an application.
        The inbound_sync_request contains the list of streams to be synchronized.
        To return results, invoke inbound_sync_request.enqueue_results() during the load process.

        :param PluginConfigurationParameters parameters the parameters of the sync, as configured by the user
        :param InboundSyncRequest inbound_sync_request an object describing what needs to be sync'd
        :return None
        :raises ValueError: if issues were encountered during connection
        """
        tenant_url = parameters.get_connection_parameter("tenant_url").value
        for stream in inbound_sync_request.streams:
            query_params = {}
            if stream.sync_strategy == InboundSyncStrategy.INCREMENTAL:
                if 'latest_modified_date' in stream.latest_state:
                    query_params['latest_modified_date'] = stream.latest_state['latest_modified_date']
            # fetch the records for the stream
            response = requests.get(
                url=f"{tenant_url}/api/v1/{stream.stream_name}",
                params=query_params,
                timeout=60,
            )
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch records: {response.status_code}")
            records = response.json()
            # get the latest modified date from the records, to update the sync state
            latest_modified_date = max([record['modified_date'] for record in records])
            # enqueue the records to be returned to Omnata
            inbound_sync_request.enqueue_results(stream_name=stream.stream_name,
                                                 results=records,
                                                 new_state={'latest_modified_date': latest_modified_date})

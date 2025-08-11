"""
A module for wrapping an Airbyte plugin
"""
import inspect
import logging
import os
import sys
import threading
import typing
from pathlib import Path
from typing import Dict, List
from zipfile import ZipFile

import yaml
from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
)
from airbyte_cdk.models.airbyte_protocol import Type
from airbyte_cdk.sources.source import Source
from omnata_plugin_runtime.configuration import (
    InboundSyncConfigurationParameters,
    InboundSyncStrategy,
    StoredStreamConfiguration,
    StreamConfiguration,
    SyncConfigurationParameters,
)
from omnata_plugin_runtime.forms import (
    ConnectionMethod,
    FormCheckboxField,
    FormInputField,
)
from omnata_plugin_runtime.omnata_plugin import (
    ConnectionConfigurationParameters,
    ConnectResponse,
    InboundSyncRequest,
    OmnataPlugin,
    PluginManifest,
    managed_inbound_processing,
)

logger = logging.getLogger("omnata_plugin")


class AirbyteWrapperPlugin(OmnataPlugin):
    """
    An Omnata plugin which wraps an Airbyte connector written using Airbyte's Python CDK.
    This file should be copied into the root of the Airbyte connector, adjacent to the main.py and requirements.txt files.
    """

    def __init__(self):
        OmnataPlugin.__init__(self)
        self.module_directory = Path(__file__)
        sys.path.append(str(self.module_directory.absolute()))
        # self.connector_module:ModuleType = self.find_airbyte_source_in_module()
        # source_submodule = getattr(self.connector_module, 'source')
        self.source_class: typing.Type[Source] = self.find_airbyte_source()
        self._unapplied_state_data = None

    def find_airbyte_source(self, module_name="main") -> Source:
        """
        Searches within an adjacent module for imported subclasses of Source
        """
        airbyte_main_module = __import__(module_name)
        for x in dir(airbyte_main_module):
            cls = getattr(airbyte_main_module, x)
            if inspect.isclass(cls) and issubclass(cls, Source):
                return cls
        raise ValueError(
            "No plugins found. Please ensure the Airbyte wrapper is located adjacent to a main.py which imports a subclass of Source"
        )

    def get_manifest(self) -> PluginManifest:
        plugin_name = self.source_class.__name__.replace("Source", "")

        return PluginManifest(
            app_id=f"airbyte_{plugin_name.lower()}",
            name=f"{plugin_name} (Airbyte)",
            docs_url="https://docs.omnata.com",
            supports_inbound=True,
            supported_outbound_strategies=[],
        )

    def additional_loggers(self):
        return ["airbyte"]

    def connection_form(self):
        # use the spec.yaml file to generate a configuration screen
        this_file = os.path.abspath(__file__)
        this_file_parent = os.path.dirname(this_file)
        with ZipFile(this_file_parent) as zip_file:
            for file in zip_file.namelist():
                if not file.endswith("spec.yaml"):
                    continue

                with zip_file.open(file) as f:
                    spec_yaml = yaml.safe_load(f)
                    connection_fields = []

                    for prop_name, prop_value in spec_yaml["connectionSpecification"][
                        "properties"
                    ].items():
                        if "title" in prop_value:
                            if prop_value["type"] in ["string", "integer", "number"]:
                                connection_fields.append(
                                    FormInputField(
                                        name=prop_name,
                                        label=prop_value["title"],
                                        default_value=prop_value["default"]
                                        if "default" in prop_value
                                        else "",
                                        help_text=prop_value["description"]
                                        if "description" in prop_value
                                        else None,
                                        required=prop_name
                                        in spec_yaml["connectionSpecification"][
                                            "required"
                                        ],
                                        secret=prop_value["airbyte_secret"]
                                        if "airbyte_secret" in prop_value
                                        else False,
                                    )
                                )
                            if prop_value["type"] == "boolean":
                                connection_fields.append(
                                    FormCheckboxField(
                                        name=prop_name,
                                        label=prop_value["title"],
                                        default_value=prop_value["default"]
                                        if "default" in prop_value
                                        else False,
                                        help_text=prop_value["description"]
                                        if "description" in prop_value
                                        else None,
                                    )
                                )
        return [ConnectionMethod(name="Airbyte form", fields=connection_fields)]

    def connect(self, parameters: ConnectionConfigurationParameters) -> ConnectResponse:
        logging.info("Connection request received")
        check_result = self.source_class().check(
            logging, self.omnata_params_to_airbyte(parameters)
        )
        if not check_result.status.value == "SUCCEEDED":
            raise ValueError(
                f"Connection check failed with message: {check_result.message}"
            )
        return ConnectResponse()

    def list_inbound_streams(
        self, parameters: InboundSyncConfigurationParameters
    ) -> List[StreamConfiguration]:
        """
        Lists the streams from the Airbyte catalog
        """
        sf_catalog = self.source_class().discover(
            logger=logger, config=self.omnata_params_to_airbyte(parameters)
        )
        streams_to_return: List[StreamConfiguration] = []
        for stream in sf_catalog.streams:
            sync_strategies: List[InboundSyncStrategy] = [
                InboundSyncStrategy.FULL_REFRESH
                if mode.name == "full_refresh"
                else InboundSyncStrategy.INCREMENTAL
                for mode in stream.supported_sync_modes
            ]
            logger.info(stream)
            streams_to_return.append(
                StreamConfiguration(
                    stream_name=stream.name,
                    supported_sync_strategies=sync_strategies,
                    source_defined_cursor=stream.source_defined_cursor,
                    default_cursor_field=stream.default_cursor_field[0]
                    if stream.default_cursor_field
                    else None,
                    source_defined_primary_key=stream.source_defined_primary_key[0][0]
                    if stream.source_defined_primary_key
                    else None,
                    json_schema=stream.json_schema,
                )
            )
        return streams_to_return

    def omnata_params_to_airbyte(self, parameters: SyncConfigurationParameters) -> dict:
        """
        Takes an Omnata SyncConfigurationParameters object and flattens it into a simple dict, suitable as Airbyte
        configuration.
        """
        return {
            k: v["value"]
            for k, v in {
                **parameters.connection_parameters,
                **parameters.connection_secrets,
            }.items()
        }

    def sync_inbound(
        self,
        parameters: InboundSyncConfigurationParameters,
        inbound_sync_request: InboundSyncRequest,
    ):
        logger.info("Inbound Sync request received")
        logger.info(f"Streams configuration {inbound_sync_request.streams}")
        self.total_streams = len(inbound_sync_request.streams)
        self.completed_streams = {}
        self.completed_streams_lock = threading.Lock()
        self.record_upload(
            inbound_sync_request.streams, parameters, inbound_sync_request
        )

    @managed_inbound_processing(concurrency=5)
    def record_upload(
        self,
        stream: StoredStreamConfiguration,
        parameters: InboundSyncConfigurationParameters,
        inbound_sync_request: InboundSyncRequest,
    ):
        """
        For a particular stream, reads it until the end is reached.
        """
        inbound_sync_request.update_activity(
            f"Completed {len(self.completed_streams)} of {self.total_streams} streams"
        )
        airbyte_streams: List[ConfiguredAirbyteStream] = []
        airbyte_stream = AirbyteStream(
            name=stream.stream_name,
            supported_sync_modes=[
                "full_refresh"
                if x == InboundSyncStrategy.FULL_REFRESH
                else "incremental"
                for x in stream.stream.supported_sync_strategies
            ],
            source_defined_primary_key=[[stream.stream.source_defined_primary_key]]
            if stream.stream.source_defined_primary_key
            else None,
            source_defined_cursor=stream.stream.source_defined_cursor,
            default_cursor_field=[stream.stream.default_cursor_field],
            json_schema=stream.stream.json_schema,
        )
        airbyte_stream = ConfiguredAirbyteStream(
            stream=airbyte_stream,
            sync_mode="full_refresh"
            if stream.sync_strategy == InboundSyncStrategy.FULL_REFRESH
            else "incremental",
            cursor_field=stream.cursor_field,
            destination_sync_mode="append",  # not relevant since we're only calling the read() function
            primary_key=stream.primary_key_field,
        )
        airbyte_streams.append(airbyte_stream)

        cac = ConfiguredAirbyteCatalog(streams=airbyte_streams)
        airbyte_logger = logging.LoggerAdapter(
            logger, {"stream_name": stream.stream_name}
        )
        stream_read_iterator = self.source_class().read(
            logger=airbyte_logger,
            config=self.omnata_params_to_airbyte(parameters),
            catalog=cac,
            state={stream.stream_name: stream.latest_state},
        )
        # with airbyte, it sends record messages and state messages separately.
        # we want to store them in Snowflake atomically.
        # So we buffer the records until we get a state message, and release them together
        records_buffer: List[Dict] = []
        try:
            while True:
                airbyte_message = next(stream_read_iterator)
                # logging.info(f'Recieved an airbyte {airbyte_message.type} message')
                if airbyte_message.type == Type.RECORD:
                    records_buffer.append(airbyte_message.record.data)
                    # results_df.drop(['attributes'],axis=1)
                if airbyte_message.type == Type.STATE:
                    records_buffer = [
                        records
                        for records in records_buffer
                        if records is not None and len(records) > 0
                    ]
                    if len(records_buffer) > 0:
                        inbound_sync_request.enqueue_results(
                            stream.stream_name,
                            records_buffer,
                            airbyte_message.state.data,
                        )
                        self._unapplied_state_data = None
                        records_buffer = []
                        logger.info(
                            f"Stream state update: {airbyte_message.state.data}"
                        )
                    else:
                        # we'd hope that state messages always follow record messages, but doesn't
                        # always seem to be the case.
                        inbound_sync_request._enqueue_state(
                            stream.stream_name, airbyte_message.state.data
                        )
                if airbyte_message.type == Type.LOG:
                    logger.log(
                        logging._nameToLevel[airbyte_message.level],
                        airbyte_message.message,
                    )
        except StopIteration:
            logger.info("End of Airbyte stream reached")
        inbound_sync_request.mark_stream_complete(stream.stream_name)
        with self.completed_streams_lock:
            self.completed_streams[stream.stream_name] = True

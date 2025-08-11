"""
A wrapper around the Snowflake app packaging/versioning commands.
"""
import json
from typing import Any, Dict

from snowflake.snowpark import Session


class PluginRegistration:
    """
    Handles registering an Omnata plugin with the Omnata app
    """

    def __init__(self, snowflake_connection: Any):
        if snowflake_connection.__class__.__name__ == "SnowflakeConnection":
            builder = Session.builder
            builder._options["connection"] = snowflake_connection
            self.session: Session = builder.create()
        elif snowflake_connection.__class__.__name__ == "Session":
            self.session: Session = snowflake_connection
        else:
            self.session: Session = Session.builder.configs(
                snowflake_connection
            ).create()

    def register_plugin(
        self, plugin_application_name: str, omnata_application_name: str
    ) -> bool:
        """
        Creates a native application package in Snowflake.
        Returns True if the package was created, False if it already existed.
        """
        # first, grant the omnata application access to the plugin application
        self.session.sql(
            f"""
            grant application role {plugin_application_name}.OMNATA_MANAGEMENT 
            to application {omnata_application_name}"""
        ).collect()
        # then we have to let Omnata know about the plugin, so that it can create the roles
        result = self.session.sql(
            f"""
            call {omnata_application_name}.API.REGISTER_PLUGIN('{plugin_application_name}')"""
        ).collect()
        registration_result: Dict = json.loads(result[0][0])

        if registration_result["success"] == False:
            raise ValueError(
                f"Plugin registration failed: {registration_result['error']}"
            )
        if "data" not in registration_result:
            raise ValueError("Plugin registration response did not include 'data'")
        if "application_role" not in registration_result["data"]:
            raise ValueError(
                "Plugin registration response did not include 'application_role'"
            )
        plugin_application_role = registration_result["data"]["application_role"]
        print(f"Plugin application role: {plugin_application_role}")
        self.session.sql(
            f"""
            grant application role {omnata_application_name}.{plugin_application_role} 
            to application {plugin_application_name}"""
        ).collect()
        print("Registration complete")

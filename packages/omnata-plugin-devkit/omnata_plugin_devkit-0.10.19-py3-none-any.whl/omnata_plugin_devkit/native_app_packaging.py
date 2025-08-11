"""
A wrapper around the Snowflake app packaging/versioning commands.
"""
from typing import Any, Literal, Optional
from snowflake.snowpark import Session


class NativeAppPackaging:
    """
    Handles Snowflake native app packaging/upgrading tasks
    """

    def __init__(self, snowflake_connection: Any, package_name: str):
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
        self.package_name = package_name

    def create_package(
        self,
        developer_role: Optional[str] = None,
        distribution: Literal["INTERNAL", "EXTERNAL"] = "INTERNAL",
        enable_release_channels: bool = False,
    ) -> bool:
        """
        Creates a native application package in Snowflake.
        Returns True if the package was created, False if it already existed.
        """
        # create application package if it doesn't exist
        app_packages = self.session.sql(
            f"""SHOW APPLICATION PACKAGES like '{self.package_name}';"""
        ).collect()
        if len(app_packages) == 0:
            self.session.sql(
                f"""CREATE APPLICATION PACKAGE {self.package_name} 
                                        DISTRIBUTION={distribution}
                                        ENABLE_RELEASE_CHANNELS={str(enable_release_channels).upper()}"""
            ).collect()
        if developer_role is not None:
            self.session.sql(
                f"""GRANT DEVELOP ON APPLICATION PACKAGE {self.package_name}
                            TO ROLE {developer_role}"""
            ).collect()
        return len(app_packages) == 0

    def create_package_version(
        self, code_database: str, code_schema: str, code_stage: str, version_name: str
    ) -> int:
        """
        Creates a native application version in Snowflake.
        Returns the patch number, which will be 0 if the version is new.
        """
        versions = self.session.sql(
            f"""SHOW VERSIONS LIKE '{version_name}' 
                                                IN APPLICATION PACKAGE {self.package_name};"""
        ).collect()
        # create package version if it doesn't exist
        if len(versions) == 0:
            self.session.sql(
                f"""ALTER APPLICATION PACKAGE {self.package_name}
                ADD VERSION {version_name} USING '@{code_database}.{code_schema}.{code_stage}'"""
            ).collect()
            return 0

        result = self.session.sql(
            f"""ALTER APPLICATION PACKAGE {self.package_name}
            ADD PATCH FOR VERSION {version_name} 
            USING '@{code_database}.{code_schema}.{code_stage}'"""
        ).collect()
        return result[0].as_dict()["patch"]

    def deploy_application(
        self,
        application_name: str,
        version_name: str,
        patch_number: Optional[int] = None,
        debug_mode: bool = True,
        authorize_telemetry_event_sharing: bool = True,
    ) -> bool:
        """
        Creates a native application in Snowflake.
        If patch_number is None, the latest patch will be used.
        Returns True if the application was created, False if it already existed and was upgraded.
        """
        if patch_number is None:
            versions = self.session.sql(
                f"""SHOW VERSIONS LIKE '{version_name}' 
                                                IN APPLICATION PACKAGE {self.package_name};"""
            ).collect()
            # sort the versions by the patch column, highest first
            versions = sorted(
                versions, key=lambda x: x.as_dict()["patch"], reverse=True
            )
            patch_number = versions[0].as_dict()["patch"]

        applications = self.session.sql(
            f"""SHOW APPLICATIONS like '{application_name}';"""
        ).collect()

        if len(applications) == 0:
            self.session.sql(
                f"""CREATE APPLICATION {application_name} 
                                        FROM APPLICATION PACKAGE {self.package_name}
                                        USING VERSION {version_name} patch {patch_number}
                                        DEBUG_MODE={str(debug_mode).upper()}
                                        AUTHORIZE_TELEMETRY_EVENT_SHARING={str(authorize_telemetry_event_sharing).upper()}"""
            ).collect()
            return True
        self.session.sql(
            f"""ALTER APPLICATION {application_name}
                            UPGRADE USING VERSION {version_name} patch {patch_number}"""
        ).collect()
        return False

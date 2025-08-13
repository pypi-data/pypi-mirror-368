# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.utils import NewCentralURLs
from pycentral.utils import ProfilesUtils
from pycentral.exceptions import (
    ParameterError,
    VerificationError,
)

from .profiles import Profiles

urls = NewCentralURLs()
profiles_utils = ProfilesUtils()

REQUIRED_ATTRIBUTES = {"hostname": ""}

RESOURCE = profiles_utils.get_resource("SYSTEM_INFO")
BULK_KEY = profiles_utils.get_bulk_key("SYSTEM_INFO")


class SystemInfo(Profiles):
    """
    Represents a System Information Profile object.

    This class provides methods to create, update, and manage System Information profiles
    in Aruba Central.

    :param hostname: Hostname for the system.
    :type hostname: str
    :param contact: Contact information for the system, defaults to None.
    :type contact: str, optional
    :param location: Location of the system, defaults to None.
    :type location: str, optional
    :param central_conn: Established Central connection object.
    :type central_conn: ArubaCentralNewBase, optional
    :param local: Dictionary containing required local keys & values used to assign the profile, defaults to {}.
    :type local: dict, optional
    """

    def __init__(
        self,
        hostname,
        local,
        central_conn=None,
        config_dict=None
    ):
        """
        Initialize a SystemInfo object.

        :param hostname: Hostname for the system.
        :type hostname: str
        :param local: Dictionary containing required local keys & values used to assign the profile.
        :type local: dict
        :param central_conn: Established Central connection object.
        :type central_conn: ArubaCentralNewBase, optional
        :param config_dict: Configuration dictionary for the profile, defaults to None.
        :type config_dict: dict, optional
        """
        if not isinstance(hostname, str):
            err_str = (
                f"Invalid value for hostname - must be of type string "
                f"- found {type(hostname)}"
            )
            raise ParameterError(err_str)
        else:
            self.hostname = hostname

        if not isinstance(local, dict):
            err_str = (
                f"Invalid value for local - must be of type dict "
                f"- found {type(local)}"
            )
            raise ParameterError(err_str)
        else:
            self.local = local

        # Populate config_dict with required and optional attributes if set
        if not config_dict:
            config_dict = self._getattrsdict(REQUIRED_ATTRIBUTES)
        else:
            self._createattrs(config_dict)

        self.config_dict = config_dict.copy()

        config_dict = {
            "hostname": hostname,
        }

        super().__init__(
            name=hostname,
            resource=RESOURCE,
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

        self.object_data["path"] = profiles_utils.fetch_profile_url("SYSTEM_INFO")
        self.object_data["resource"] = RESOURCE
        self.object_data["bulk_key"] = BULK_KEY

        if not central_conn:
            exit(
                "Unable to fetch SystemInfo Profile without central connection. "
                + "Please pass a central connection to SystemInfo Profile."
            )

        # Attribute used to know if object exists within Central or not
        self.materialized = False
        # Attribute used to know if object was changed recently
        self.__modified = False

    def apply(self):
        """
        Main method used to update or create a SystemInfo Profile.

        Checks whether the SystemInfo Profile exists in Central. Calls
        self.update() if SystemInfo Profile is being updated.
        Calls self.create() if a SystemInfo Profile is being created.

        :return: True if the object was created or modified.
        :rtype: bool
        """
        modified = False
        if self.materialized:
            modified = self.update()
        else:
            modified = self.create()
        # Set internal attribute
        self.__modified = modified
        return modified

    def create(self):
        """
        Perform a POST call to create a SystemInfo Profile.

        :return: True if the SystemInfo profile was created successfully.
        :rtype: bool
        """
        if not self.hostname:
            raise VerificationError("Missing self.hostname attribute", "create() failed")

        return super().create()

    def update(self):
        """
        Perform a PATCH call to apply changes to an existing SystemInfo Profile.
        Source of truth is self.config_dict.

        :return: True if the object was modified and the PATCH request was successful.
        :rtype: bool
        """
        if not set(REQUIRED_ATTRIBUTES.keys()).issubset(dir(self)) and not set(
            REQUIRED_ATTRIBUTES.keys()
        ).issubset(self.config_dict.keys()):
            raise VerificationError("Missing REQUIRED attributes", "update() failed")

        return super().update()

    def set_hostname(self, hostname):
        """
        Sets the attribute of self.hostname.

        :param hostname: Hostname for the system.
        :type hostname: str
        :return: None
        """
        if not isinstance(hostname, str):
            raise ParameterError(f"Invalid value for hostname - must be of type str, found {type(hostname)}")
        self.hostname = hostname
        self.config_dict["hostname"] = hostname

    @staticmethod
    def create_system_info(central_conn, config_dict, local):
        """
        Create a SystemInfo Profile using a configuration dictionary as input.

        :param central_conn: Established Central connection object.
        :type central_conn: ArubaCentralNewBase
        :param config_dict: Configuration dictionary for the profile.
        :type config_dict: dict
        :param local: Dictionary containing required local keys & values used to assign the profile.
        :type local: dict
        :return: True if the SystemInfo profile was created successfully.
        :rtype: bool
        """
        if not isinstance(config_dict, dict):
            err_str = (
                f"Invalid value for config_dict - must be of type dict "
                f"- found {type(config_dict)}"
            )
            raise ParameterError(err_str)
        elif not config_dict:
            err_str = (
                "Invalid value for config_dict - must have at least one key "
                "- found none"
            )
            raise ParameterError(err_str)

        return Profiles.create_profile(
            bulk_key=BULK_KEY,
            path=profiles_utils.fetch_profile_url("SYSTEM_INFO"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def get_system_info(central_conn, local):
        """
        Retrieve a SystemInfo Profile using the provided parameters.

        :param central_conn: Established Central connection object.
        :type central_conn: ArubaCentralNewBase
        :param local: Dictionary containing required local keys & values used to assign the profile.
        :type local: dict
        :return: Dictionary of the SystemInfo profile if present, None otherwise.
        :rtype: dict
        """
        return Profiles.get_profile(
            path=profiles_utils.fetch_profile_url("SYSTEM_INFO"),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_system_info(central_conn, config_dict, local):
        """
        Update a SystemInfo Profile using the provided parameters.

        :param central_conn: Established Central connection object.
        :type central_conn: ArubaCentralNewBase
        :param hostname: Hostname for the system.
        :type hostname: str
        :param contact: Contact information for the system, defaults to None.
        :type contact: str, optional
        :param location: Location of the system, defaults to None.
        :type location: str, optional
        :param local: Dictionary containing required local keys & values used to assign the profile.
        :type local: dict, optional
        :return: True if the SystemInfo profile was updated successfully.
        :rtype: bool
        """
        if not isinstance(config_dict, dict):
            err_str = (
                f"Invalid value for config_dict - must be of type dict "
                f"- found {type(config_dict)}"
            )
            raise ParameterError(err_str)
        elif not config_dict:
            err_str = (
                "Invalid value for config_dict - must have at least one key "
                "- found none"
            )
            raise ParameterError(err_str)
        
        return Profiles.update_profile(
            bulk_key=BULK_KEY,
            path=profiles_utils.fetch_profile_url("SYSTEM_INFO"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )
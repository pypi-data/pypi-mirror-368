# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.utils import ProfilesUtils
from pycentral.exceptions import (
    ParameterError,
    VerificationError,
)

from .profiles import Profiles

profile_utils = ProfilesUtils()

REQUIRED_ATTRIBUTES = {
    "ssid": "",
    "opmode": "",
    "enable": True,
    "forward-mode": "",
    "default-role": "",
}

RESOURCE = profile_utils.get_resource("WLAN")
BULK_KEY = profile_utils.get_bulk_key("WLAN")


class Wlan(Profiles):
    def __init__(
        self,
        ssid,
        opmode,
        essid_name=None,
        enable=True,
        forward_mode=None,
        default_role=None,
        personal_security=None,
        central_conn=None,
        config_dict={},
        local={},
    ):
        """
        Instantiate a WLAN SSID Profile object

        :param ssid: SSID (network name) of the WLAN profile
        :type ssid: str
        :param opmode: Operating mode of the WLAN (e.g., "WPA2_PERSONAL")
        :type opmode: str
        :param essid_name: Name that uniquely identifies the wireless network, defaults to None
        :type essid_name: str, optional
        :param enable: Whether the SSID is enabled, defaults to True
        :type enable: bool, optional
        :param forward_mode: Forwarding mode (e.g., "FORWARD_MODE_L2"), defaults to None
        :type forward_mode: str, optional
        :param default_role: Default role assigned to clients, defaults to None
        :type default_role: str, optional
        :param personal_security: Dictionary containing WPA security settings, defaults to None
        :type personal_security: dict, optional
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`
        :param config_dict: dictionary containing API keys & values used to
                           configure the WLAN profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
                     to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        """
        # Required Validation of Attributes
        if not isinstance(ssid, str):
            err_str = (
                f"invalid value for ssid - must be of type str "
                f"- found {type(ssid)}"
            )
            raise ParameterError(err_str)
        else:
            self.ssid = ssid

        if not isinstance(opmode, str):
            err_str = (
                f"invalid value for opmode - must be of type str "
                f"- found {type(opmode)}"
            )
            raise ParameterError(err_str)
        else:
            self.opmode = opmode

        if essid_name is not None and not isinstance(essid_name, str):
            err_str = (
                f"invalid value for essid_name - must be of type str "
                f"- found {type(essid_name)}"
            )
            raise ParameterError(err_str)
        else:
            self.essid_name = essid_name

        if not isinstance(enable, bool):
            err_str = (
                f"invalid value for enable - must be of type bool "
                f"- found {type(enable)}"
            )
            raise ParameterError(err_str)
        else:
            self.enable = enable

        if forward_mode is not None and not isinstance(forward_mode, str):
            err_str = (
                f"invalid value for forward_mode - must be of type str "
                f"- found {type(forward_mode)}"
            )
            raise ParameterError(err_str)
        else:
            self.forward_mode = forward_mode

        if default_role is not None and not isinstance(default_role, str):
            err_str = (
                f"invalid value for default_role - must be of type str "
                f"- found {type(default_role)}"
            )
            raise ParameterError(err_str)
        else:
            self.default_role = default_role

        if personal_security is not None and not isinstance(
            personal_security, dict
        ):
            err_str = (
                f"invalid value for personal_security - must be of type dict "
                f"- found {type(personal_security)}"
            )
            raise ParameterError(err_str)
        else:
            self.personal_security = personal_security

        # Populate config_dict with required and optional attributes if set
        if not config_dict:
            config_dict = {
                "ssid": self.ssid,
                "opmode": self.opmode,
                "enable": self.enable,
            }

            if essid_name:
                config_dict["essid"] = {"name": essid_name}

            if forward_mode:
                config_dict["forward-mode"] = forward_mode

            if default_role:
                config_dict["default-role"] = default_role

            if personal_security:
                config_dict["personal-security"] = personal_security
        else:
            self._createattrs(config_dict)

        self.config_dict = config_dict

        super().__init__(
            name=self.ssid,
            resource=RESOURCE,
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

        self.object_data["path"] = profile_utils.fetch_profile_url(
            "WLAN", str(self.ssid)
        )
        self.resource = RESOURCE
        self.object_data["bulk_key"] = BULK_KEY

        # Attribute used to know if object exists within Central or not
        self.materialized = False
        # Attribute used to know if object was changed recently
        self.__modified = False

    def create(self):
        """
        Perform a POST call to create a WLAN Profile. Only returns if
        no exception is raised.

        :return: var wlan_creation_status - True if WLAN profile was created.
        :rtype: bool
        """
        if not self.ssid:
            err_str = "Missing self.ssid attribute"
            raise VerificationError(err_str, "create() failed")

        return super().create()

    def update(self):
        """
        Perform a POST call to apply changes to an existing WLAN Profile.
        Source of truth is self. Perform a POST call to apply difference
        found in self to an existing WLAN Profile.

        :return: var modified: True if Object was modified and a POST request
                was successful.
        :rtype: bool
        """
        if not self.ssid:
            err_str = "Missing self.ssid attribute"
            raise VerificationError(err_str, "update() failed")

        return super().update()

    def set_ssid(self, ssid):
        """
        Sets the attribute of self.ssid

        :param ssid: SSID (network name) of the WLAN
        :type ssid: str
        :return: None
        :raises ParameterError: If ssid is not of type str
        """
        if not isinstance(ssid, str):
            err_str = (
                f"invalid value for ssid - must be of type str "
                f"- found {type(ssid)}"
            )
            raise ParameterError(err_str)
        self.ssid = ssid
        self.config_dict["ssid"] = ssid

    def set_opmode(self, opmode):
        """
        Sets the operating mode of the WLAN

        :param opmode: Operating mode (e.g., "WPA2_PERSONAL")
        :type opmode: str
        :return: None
        :raises ParameterError: If opmode is not of type str
        """
        if not isinstance(opmode, str):
            err_str = (
                f"invalid value for opmode - must be of type str "
                f"- found {type(opmode)}"
            )
            raise ParameterError(err_str)
        self.opmode = opmode
        self.config_dict["opmode"] = opmode

    def set_essid(self, essid_name):
        """
        Sets the ESSID name for the WLAN

        :param essid_name: Name that uniquely identifies the wireless network
        :type essid_name: str
        :return: None
        :raises ParameterError: If essid_name is not of type str
        """
        if not isinstance(essid_name, str):
            err_str = (
                f"invalid value for essid_name - must be of type str "
                f"- found {type(essid_name)}"
            )
            raise ParameterError(err_str)
        self.essid_name = essid_name

        if "essid" not in self.config_dict:
            self.config_dict["essid"] = {}

        self.config_dict["essid"]["name"] = essid_name

    def set_enable(self, enable):
        """
        Sets whether the WLAN is enabled

        :param enable: Whether the SSID is enabled
        :type enable: bool
        :return: None
        :raises ParameterError: If enable is not of type bool
        """
        if not isinstance(enable, bool):
            err_str = (
                f"invalid value for enable - must be of type bool "
                f"- found {type(enable)}"
            )
            raise ParameterError(err_str)
        self.enable = enable
        self.config_dict["enable"] = enable

    def set_forward_mode(self, forward_mode):
        """
        Sets the forwarding mode for the WLAN

        :param forward_mode: Forwarding mode (e.g., "FORWARD_MODE_L2")
        :type forward_mode: str
        :return: None
        :raises ParameterError: If forward_mode is not of type str
        """
        if not isinstance(forward_mode, str):
            err_str = (
                f"invalid value for forward_mode - must be of type str "
                f"- found {type(forward_mode)}"
            )
            raise ParameterError(err_str)
        self.forward_mode = forward_mode
        self.config_dict["forward-mode"] = forward_mode

    def set_default_role(self, default_role):
        """
        Sets the default role for the WLAN

        :param default_role: Default role assigned to clients
        :type default_role: str
        :return: None
        :raises ParameterError: If default_role is not of type str
        """
        if not isinstance(default_role, str):
            err_str = (
                f"invalid value for default_role - must be of type str "
                f"- found {type(default_role)}"
            )
            raise ParameterError(err_str)
        self.default_role = default_role
        self.config_dict["default-role"] = default_role

    def set_personal_security(self, personal_security):
        """
        Sets the personal security settings for the WLAN

        :param personal_security: Dictionary containing WPA security settings
        :type personal_security: dict
        :return: None
        :raises ParameterError: If personal_security is not of type dict
        """
        if not isinstance(personal_security, dict):
            err_str = (
                f"invalid value for personal_security - must be of type dict "
                f"- found {type(personal_security)}"
            )
            raise ParameterError(err_str)
        self.personal_security = personal_security
        self.config_dict["personal-security"] = personal_security

    def set_vlan_settings(self, vlan_id_range, vlan_selector="VLAN_RANGES"):
        """
        Sets the VLAN settings for the WLAN

        :param vlan_id_range: List of VLAN IDs to assign to the WLAN
        :type vlan_id_range: list
        :param vlan_selector: Type of VLAN selection, defaults to "VLAN_RANGES"
        :type vlan_selector: str, optional
        :return: None
        :raises ParameterError: If parameters are not of the correct type
        """
        if not isinstance(vlan_id_range, list):
            err_str = (
                f"invalid value for vlan_id_range - must be of type list "
                f"- found {type(vlan_id_range)}"
            )
            raise ParameterError(err_str)

        if not isinstance(vlan_selector, str):
            err_str = (
                f"invalid value for vlan_selector - must be of type str "
                f"- found {type(vlan_selector)}"
            )
            raise ParameterError(err_str)

        self.config_dict["vlan-id-range"] = vlan_id_range
        self.config_dict["vlan-selector"] = vlan_selector

    def get_resource_str(self):
        """
        Returns the resource string for the WLAN profile

        :return: String representation of the resource path
        :rtype: str
        """
        return f"{self.resource}/{self.ssid}"

    @staticmethod
    def get_resource():
        """
        Returns the resource type for WLAN profiles

        :return: Resource type
        :rtype: str
        """
        return RESOURCE

    @staticmethod
    def create_wlan(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Create a WLAN using the provided parameters.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param config_dict: dictionary containing API keys & values used to
                           configure the WLAN profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
                     to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if WLAN was created successfully, False otherwise.
        :rtype: bool
        """
        config_dict = config_dict.copy()

        return Profiles.create_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("WLAN"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def get_wlan(ssid, central_conn, local={}):
        """
        GET a WLAN using the provided parameters.

        :param ssid: SSID (network name) of the WLAN
        :type ssid: str
        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param local: dictionary containing required local keys & values used
                     to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: dict of WLAN if present, None otherwise.
        :rtype: dict
        """
        # Validate parameters
        if not isinstance(ssid, str):
            raise ParameterError(
                f"Invalid value for ssid - must be of type str, found {type(ssid)}"
            )

        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("WLAN", ssid),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_wlan(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Update a WLAN using the provided parameters.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param config_dict: dictionary containing API keys & values used to
                           configure the WLAN profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
                     to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if WLAN was updated successfully, False otherwise.
        :rtype: bool
        """
        config_dict = config_dict.copy()

        return Profiles.update_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("WLAN"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def delete_wlan(ssid, central_conn, local={}):
        """
        Delete a WLAN using the provided parameters.

        :param ssid: SSID (network name) of the WLAN to delete
        :type ssid: str
        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param local: dictionary containing required local keys & values used
                     to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if WLAN was deleted successfully, False otherwise
        :rtype: bool
        """
        # Validate parameters
        if not isinstance(ssid, str):
            raise ParameterError(
                f"Invalid value for ssid - must be of type str, found {type(ssid)}"
            )

        result = Profiles.delete_profile(
            path=profile_utils.fetch_profile_url("WLAN", ssid),
            central_conn=central_conn,
            local=local,
        )

        return result

    @staticmethod
    def create_wlans(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Create multiple WLAN profiles in a single API call using a POST
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param list_dict: List of WLAN profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of WLAN objects containing the config_dict attribute, defaults to None.
        :type list_obj: list, optional required if list_dict is not provided
        :param local: Dictionary containing local keys & values used to assign the profile, defaults to {}.
        :type local: dict, optional

        :raises ParameterError: If neither list_dict nor list_obj is provided.
        :return: True if profiles were successfully created, False otherwise.
        :rtype: bool
        """
        if not list_dict and not list_obj:
            err_str = "either list_dict or list_obj must be provided"
            raise ParameterError(err_str)

        result = Profiles.create_profiles(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("WLAN"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def get_wlans(central_conn, local={}):
        """
        GET all WLANs using the provided parameters.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param local: dictionary containing required local keys & values used
                     to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional

        :return: dict of WLANs if present, None otherwise.
        :rtype: dict
        """
        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("WLAN"),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_wlans(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Update multiple WLAN profiles in a single API call using a PATCH
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param list_dict: List of profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of WLAN objects containing the config_dict attribute, defaults to None.
        :type list_obj: list, optional required if list_dict is not provided
        :param local: dictionary containing required local keys & values used
                     to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional

        :raises ParameterError: If neither list_dict nor list_obj is provided.
        :return: True if profiles were successfully updated, False otherwise.
        :rtype: bool
        """
        if not list_dict and not list_obj:
            err_str = "either list_dict or list_obj must be provided"
            raise ParameterError(err_str)

        result = Profiles.update_profiles(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("WLAN"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def delete_wlans(
        central_conn, list_ssid_names=None, list_wlan_obj=None, local={}
    ):
        """
        Delete multiple WLAN profiles through multiple API calls using
        a DELETE request.

        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`
        :param list_ssid_names: List of SSID names to be deleted, defaults to None.
        :type list_ssid_names: list, required if list_wlan_obj is not provided
        :param list_wlan_obj: List of WLAN objects containing the object_data attribute, defaults to None.
        :type list_wlan_obj: list, optional required if list_ssid_names is not provided
        :param local: dictionary containing required local keys & values used
                     to remove the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional

        :raises ParameterError: If neither list_ssid_names nor list_wlan_obj is provided.
        :return: Empty if profiles were successfully deleted, populated otherwise.
        :rtype: list
        """
        path_list = []
        if not list_ssid_names and not list_wlan_obj:
            err_str = (
                "either list_ssid_names or list_wlan_obj must be provided"
            )
            raise ParameterError(err_str)

        if list_ssid_names:
            for item in list_ssid_names:
                if not isinstance(item, str):
                    err_str = f"Invalid value in list_ssid_names - all items must be of type str, found {type(item)}"
                    raise ParameterError(err_str)
                else:
                    path_list.append(
                        profile_utils.fetch_profile_url("WLAN", item)
                    )

        elif list_wlan_obj:
            for profile in list_wlan_obj:
                if not isinstance(profile, Wlan):
                    err_str = f"Invalid value in list_wlan_obj - all items must be of type Wlan, found {type(profile)}"
                    raise ParameterError(err_str)

                path_list.append(profile.object_data["path"])

        result = Profiles.delete_profiles(
            path_list=path_list, central_conn=central_conn, local=local
        )
        return result

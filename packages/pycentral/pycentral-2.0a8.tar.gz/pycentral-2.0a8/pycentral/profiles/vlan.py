# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.utils import ProfilesUtils
from pycentral.exceptions import (
    ParameterError,
    VerificationError,
)

from .profiles import Profiles

profile_utils = ProfilesUtils()

REQUIRED_ATTRIBUTES = {"vlan": 0}

RESOURCE = profile_utils.get_resource("VLAN")
BULK_KEY = profile_utils.get_bulk_key("VLAN")


class Vlan(Profiles):
    def __init__(
        self,
        vlan,
        description=None,
        name=None,
        central_conn=None,
        config_dict={},
        local={},
    ):
        """
        instantiate a VLAN Profile object

        :param vlan: id of the vlan profile
        :type vlan: int
        :param description: description of VLAN profile, defaults to None
        :type description: str, optional
        :param name: name of the VLAN profile, defaults to None
        :type name: str, optional
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param config_dict: dictionary containing API keys & values used to
        configure the VLAN profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        """
        # Required Validation of Attributes
        if not isinstance(vlan, int):
            err_str = (
                f"invalid value for vlan - must be of type int "
                f"- found {type(vlan)}"
            )
            raise ParameterError(err_str)
        else:
            self.vlan = vlan

        if description is not None and not isinstance(description, str):
            err_str = (
                f"invalid value for description - must be of type str "
                f"- found {type(description)}"
            )
            raise ParameterError(err_str)
        else:
            self.description = description

        if name is not None and not isinstance(name, str):
            err_str = (
                f"invalid value for name - must be of type str "
                f"- found {type(name)}"
            )
            raise ParameterError(err_str)
        else:
            self.name = name

        # Populate config_dict with required and optional attributes if set
        if not config_dict:
            config_dict = self._getattrsdict(REQUIRED_ATTRIBUTES)

            if description:
                config_dict["description"] = description
            if name:
                config_dict["name"] = name
        else:
            self._createattrs(config_dict)

        self.config_dict = config_dict.copy()

        super().__init__(
            name=self.name,
            resource=RESOURCE,
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

        self.object_data["path"] = profile_utils.fetch_profile_url(
            "VLAN", str(self.vlan)
        )
        self.resource = RESOURCE
        self.object_data["bulk_key"] = BULK_KEY

        # Attribute used to know if object exists within Central or not
        self.materialized = False
        # Attribute used to know if object was changed recently
        self.__modified = False

    def apply(self):
        """
        Main method used to update or create a Vlan Profile.
            Checks whether the Vlan Profile exists in Central. Calls
            self.update() if Vlan Profile is being updated.
            Calls self.create() if a Vlan Profile is being created.
        :return: var modified - True if object was created or modified.
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
        Perform a POST call to create a Layer 2 Vlan Profile. Only returns if
            no exception is raised.
        :return: var vlan_creation_status - True if Vlan profile was created.
        :rtype: bool
        """
        if not self.vlan:
            err_str = "Missing self.vlan attribute"
            raise VerificationError(err_str, "create() failed")

        return super().create()

    def update(self):
        """
        Perform a POST call to apply changes to an existing Vlan Profile.
            Source of truth is self.config_dict
        Perform a POST call to apply difference found in self.config_dict to an existing
            Vlan Profile.
        :return: var modified: True if Object was modified and a POST request
        was successful.
        :rtype: bool
        """
        if not set(REQUIRED_ATTRIBUTES.keys()).issubset(dir(self)) and not set(
            REQUIRED_ATTRIBUTES.keys()
        ).issubset(self.config_dict.keys()):
            err_str = "Missing REQUIRED attributes"
            raise VerificationError(err_str, "update() failed")

        return super().update()

    def set_vlan(self, vlan_id):
        """
        Sets the attribute of self.vlan
        :return: None
        """
        if not isinstance(vlan_id, int):
            err_str = (
                f"invalid value for vlan_id - must be of type int "
                f"- found {type(vlan_id)}"
            )
            raise ParameterError(err_str)
        self.vlan = vlan_id
        self.config_dict["vlan"] = vlan_id

    def set_description(self, description):
        """
        Sets the attribute of self.description
        :return: None
        """
        if not isinstance(description, str):
            err_str = (
                f"invalid value for description - must be of type str "
                f"- found {type(description)}"
            )
            raise ParameterError(err_str)
        self.description = description
        self.config_dict["description"] = description

    def get_resource_str(self):
        return f"{self.resource}/{self.vlan}"

    @staticmethod
    def get_resource():
        return RESOURCE

    @staticmethod
    def get_bulk_key():
        return BULK_KEY

    @staticmethod
    def create_vlan(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Create a VLAN using the provided parameters.

        :param vlan: int
            The VLAN identifier (1-4094).
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param config_dict: dictionary containing API keys & values used to
        configure the VLAN profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        :raises ParameterError: If any parameter is of invalid type.
        :return: True if Vlan was created successfully, False otherwise.
        :rtype: bool
        """

        config_dict = config_dict.copy()

        return Profiles.create_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("VLAN"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def get_vlan(vlan, central_conn, local={}):
        """
        GET a VLAN using the provided parameters.

        :param vlan: int
            The VLAN identifier (1-4094).
        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        :raises ParameterError: If any parameter is of invalid type.
        :return: dict of Vlan if present, None otherwise.
        :rtype: dict
        """
        # Validate parameters
        if not isinstance(vlan, int):
            raise ParameterError(
                f"Invalid value for vlan - must be of type int, found {type(vlan)}"
            )

        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("VLAN", str(vlan)),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_vlan(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Update a VLAN using the provided parameters.

        :param vlan: int
            The VLAN identifier (1-4094).
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param config_dict: dictionary containing API keys & values used to
        configure the VLAN profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing local keys & values used to assign
        the profile, see profiles.py for more details, defaults to {}
        :type local: dict, optional
        :raises ParameterError: If any parameter is of invalid type.
        :return: dict
            The response from the API.
        """

        config_dict = config_dict.copy()

        return Profiles.update_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("VLAN"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def delete_vlan(vlan, central_conn, local={}):
        """
        Delete a VLAN using the provided parameters.

        :param vlan: int
            The VLAN identifier (1-4094).
        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase,
        :return: dict
            The response from the API.

        :raises ParameterError: If any parameter is of invalid type.
        """

        # Validate parameters
        if not isinstance(vlan, int):
            raise ParameterError(
                f"Invalid value for vlan - must be of type int, found {type(vlan)}"
            )

        result = Profiles.delete_profile(
            path=profile_utils.fetch_profile_url("VLAN", str(vlan)),
            central_conn=central_conn,
            local=local,
        )

        return result

    @staticmethod
    def create_vlans(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Create multiple Vlan profiles in a single API call using a POST
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param list_dict: List of Vlan profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of Vlan objects containing the config_dict attribute, defaults to None.
        :type list_obj: list, optional required if list_dict is not provided
        :raises ParameterError: If neither list_dict nor list_obj is provided.
        :param local: Dictionary containing local keys & values used to assign the profile, defaults to None.
        :type local: dict, optional
        :return: True if profiles were successfully created, False otherwise.
        :rtype: bool
        """

        if not list_dict and not list_obj:
            err_str = "either list_dict or list_obj must be provided"
            raise ParameterError(err_str)

        result = Profiles.create_profiles(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("VLAN"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def get_vlans(central_conn, local={}):
        """
        GET all VLANs using the provided parameters.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "ACCESS_SWITCH"}
        :type local: dict, optional
        :raises ParameterError: If any parameter is of invalid type.
        :return: dict of Vlan if present, None otherwise.
        :rtype: dict
        """
        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("VLAN"),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_vlans(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Update multiple Vlan profiles in a single API call using a PATCH
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param list_dict: List of profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of Profiles objects containing the config_dict attribute, defaults to None.
        :type list_obj: list, optional required if list_dict is not provided
        :raises ParameterError: If neither list_dict nor list_obj is provided.
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        :return: True if profiles were successfully created, False otherwise.
        :rtype: bool
        """
        if not list_dict and not list_obj:
            err_str = "either list_dict or list_obj must be provided"
            raise ParameterError(err_str)

        result = Profiles.update_profiles(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("VLAN"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def delete_vlans(
        central_conn, list_vlan_ids=None, list_vlan_obj=None, local={}
    ):
        """
        Delete multiple configuration profiles through multiple API calls using
        a DELETE request.

        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :param list_vlan_ids: List of of Vlan IDs to be deleted, defaults to None.
        :type list_vlan_ids: list, required if list_vlan_obj is not provided
        :param list_vlan_obj: List of Vlan objects containing the object_data attribute, defaults to None.
        :type list_vlan_obj: list, optional required if list_vlan_ids is not provided
        :raises ParameterError: If neither list_vlan_ids nor list_vlan_obj is provided.
        :param local: dictionary containing required local keys & values used
        to remove the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        :param error_on_fail: list of API paths as type string for requests.
        :type error_on_fail: bool, optional
        :return: Empty if profiles were successfully deleted, populated otherwise.
        :rtype: list
        """
        path_list = []
        if not list_vlan_ids and not list_vlan_obj:
            err_str = "either list_str or list_obj must be provided"
            raise ParameterError(err_str)

        if list_vlan_ids:
            for item in list_vlan_ids:
                if not isinstance(item, int):
                    err_str = f"Invalid value in list_str - all items must be of type int, found {type(item)}"
                    raise ParameterError(err_str)
                else:
                    path_list.append(
                        profile_utils.fetch_profile_url("VLAN", str(item))
                    )

        elif list_vlan_obj:
            for profile in list_vlan_obj:
                if not isinstance(profile, Vlan):
                    err_str = f"Invalid value in list_vlan_obj - all items must be of type Vlan, found {type(profile)}"
                    raise ParameterError(err_str)

                path_list.append(profile.object_data["path"])

        result = Profiles.delete_profiles(
            path_list=path_list, central_conn=central_conn, local=local
        )
        return result

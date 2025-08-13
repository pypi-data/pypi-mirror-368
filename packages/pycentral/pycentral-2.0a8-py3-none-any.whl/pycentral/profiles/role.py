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
profile_utils = ProfilesUtils()

REQUIRED_ATTRIBUTES = {"name": ""}

RESOURCE = profile_utils.get_resource("ROLE")
BULK_KEY = profile_utils.get_bulk_key("ROLE")


class Role(Profiles):
    def __init__(
        self,
        name,
        description=None,
        central_conn=None,
        config_dict={},
        local={},
    ):
        """
        Instantiate a Role Profile object

        :param name: name of the role profile (required)
        :type name: str
        :param description: description of role profile, defaults to None
        :type description: str, optional
        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase, optional
        :param config_dict: dictionary containing API keys & values used to
        configure the role profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional
        """
        # Required Validation of Attributes
        if not isinstance(name, str):
            err_str = (
                f"invalid value for name - must be of type str "
                f"- found {type(name)}"
            )
            raise ParameterError(err_str)
        else:
            self.name = name

        if description is not None and not isinstance(description, str):
            err_str = (
                f"invalid value for description - must be of type str "
                f"- found {type(description)}"
            )
            raise ParameterError(err_str)
        else:
            self.description = description

        # Populate config_dict with required and optional attributes if set
        if not config_dict:
            config_dict = self._getattrsdict(REQUIRED_ATTRIBUTES)
            if description:
                config_dict["description"] = description
        else:
            self._createattrs(config_dict)

        self.config_dict = config_dict

        super().__init__(
            name=self.name,
            resource=RESOURCE,
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

        self.object_data["path"] = profile_utils.fetch_profile_url(
            "ROLE", str(self.name)
        )
        self.resource = RESOURCE
        self.object_data["bulk_key"] = BULK_KEY

        if not central_conn:
            exit(
                "Unable to fetch Role Profile without central connection. "
                + "Please pass a central connection to Role Profile."
            )

        # Attribute used to know if object exists within Central or not
        self.materialized = False
        # Attribute used to know if object was changed recently
        self.__modified = False

    def create(self):
        """
        Perform a POST call to create a Role Profile. Only returns if
        no exception is raised.

        :return: var role_creation_status - True if Role profile was created.
        :rtype: bool
        """
        if not self.name:
            err_str = "Missing self.name attribute"
            raise VerificationError(err_str, "create() failed")

        return super().create()

    def update(self):
        """
        Perform a POST call to apply changes to an existing Role Profile.
        Source of truth is self. Perform a POST call to apply difference
        found in self to an existing Role Profile.

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

    def set_name(self, name):
        """
        Sets the attribute of self.name

        :param name: Name of role profile
        :type name: str
        :return: None
        :raises ParameterError: If name is not of type str
        """
        if not isinstance(name, str):
            err_str = (
                f"invalid value for name - must be of type str "
                f"- found {type(name)}"
            )
            raise ParameterError(err_str)
        self.name = name
        self.config_dict["name"] = name

    def set_description(self, description):
        """
        Sets the attribute of self.description

        :param description: Description of role profile
        :type description: str
        :return: None
        :raises ParameterError: If description is not of type str
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
        """
        Returns the resource string for the role profile

        :return: String representation of the resource path
        :rtype: str
        """
        return f"{self.resource}/{self.name}"

    @staticmethod
    def get_resource():
        """
        Returns the resource type for role profiles

        :return: Resource type
        :rtype: str
        """
        return RESOURCE

    @staticmethod
    def create_role(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Create a role using the provided parameters.

        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param config_dict: dictionary containing API keys & values used to
        configure the role profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if Role was created successfully, False otherwise.
        :rtype: bool
        """
        config_dict = config_dict.copy()

        return Profiles.create_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("ROLE"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def get_role(name, central_conn, local={}):
        """
        GET a Role using the provided parameters.

        :param name: name of the role profile
        :type name: str
        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: dict of Role if present, None otherwise.
        :rtype: dict
        """
        # Validate parameters
        if not isinstance(name, str):
            raise ParameterError(
                f"Invalid value for name - must be of type str, found {type(name)}"
            )

        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("ROLE", name),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_role(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Update a Role using the provided parameters.

        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param name: Role name (1-63 characters)
        :type name: str
        :param description: Description of the role profile (1-256 characters)
        :type description: str, optional
        :param config_dict: dictionary containing API keys & values used to
        configure the role profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if role was updated successfully, False otherwise.
        :rtype: bool
        """
        config_dict = config_dict.copy()

        return Profiles.update_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("ROLE"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def delete_role(name, central_conn, local={}):
        """
        Delete a Role using the provided parameters.

        :param name: Role name to delete
        :type name: str
        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if role was deleted successfully, False otherwise
        :rtype: bool
        """
        # Validate parameters
        if not isinstance(name, str):
            raise ParameterError(
                f"Invalid value for name - must be of type str, found {type(name)}"
            )

        result = Profiles.delete_profile(
            path=profile_utils.fetch_profile_url("ROLE", name),
            central_conn=central_conn,
            local=local,
        )

        return result

    @staticmethod
    def create_roles(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Create multiple Role profiles in a single API call using a POST
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param list_dict: List of Role profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of Role objects containing the config_dict attribute, defaults to None.
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
            path=profile_utils.fetch_profile_url("ROLE"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def get_roles(central_conn, local={}):
        """
        GET all Roles using the provided parameters.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :return: dict of Roles if present, None otherwise.
        :rtype: dict
        """
        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("ROLE"),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_roles(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Update multiple Role profiles in a single API call using a PATCH
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param list_dict: List of profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of Role objects containing the config_dict attribute, defaults to None.
        :type list_obj: list, optional required if list_dict is not provided
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
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
            path=profile_utils.fetch_profile_url("ROLE"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def delete_roles(
        central_conn, list_role_names=None, list_role_obj=None, local={}
    ):
        """
        Delete multiple Role profiles through multiple API calls using
        a DELETE request.

        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`
        :param list_role_names: List of Role names to be deleted, defaults to None.
        :type list_role_names: list, required if list_role_obj is not provided
        :param list_role_obj: List of Role objects containing the object_data attribute, defaults to None.
        :type list_role_obj: list, optional required if list_role_names is not provided
        :param local: dictionary containing required local keys & values used
        to remove the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If neither list_role_names nor list_role_obj is provided.
        :return: Empty if profiles were successfully deleted, populated otherwise.
        :rtype: list
        """
        path_list = []
        if not list_role_names and not list_role_obj:
            err_str = (
                "either list_role_names or list_role_obj must be provided"
            )
            raise ParameterError(err_str)

        if list_role_names:
            for item in list_role_names:
                if not isinstance(item, str):
                    err_str = f"Invalid value in list_role_names - all items must be of type str, found {type(item)}"
                    raise ParameterError(err_str)
                else:
                    path_list.append(
                        profile_utils.fetch_profile_url("ROLE", item)
                    )

        elif list_role_obj:
            for profile in list_role_obj:
                if not isinstance(profile, Role):
                    err_str = f"Invalid value in list_role_obj - all items must be of type Role, found {type(profile)}"
                    raise ParameterError(err_str)

                path_list.append(profile.object_data["path"])

        result = Profiles.delete_profiles(
            path_list=path_list, central_conn=central_conn, local=local
        )
        return result

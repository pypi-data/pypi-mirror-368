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

REQUIRED_ATTRIBUTES = {"name": "", "type": ""}

RESOURCE = profile_utils.get_resource("POLICY")
BULK_KEY = profile_utils.get_bulk_key("POLICY")


class Policy(Profiles):
    def __init__(
        self,
        name,
        policy_type=None,
        description=None,
        association=None,
        security_policy=None,
        central_conn=None,
        config_dict={},
        local={},
    ):
        """
        Instantiate a Policy Profile object.

        :param name: The name of the policy.
        :type name: str
        :param policy_type: The type of the policy (e.g., "POLICY_TYPE_SECURITY"), defaults to None.
        :type policy_type: str
        :param description: Description or comment for the policy, defaults to None.
        :type description: str, optional
        :param association: Policy association type (e.g., "ASSOCIATION_ROLE"), defaults to None.
        :type association: str, optional
        :param security_policy: Security policy configuration, defaults to None.
        :type security_policy: dict, optional
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param config_dict: Dictionary containing API keys & values used to configure the policy, defaults to {}.
        :type config_dict: dict, optional
        :param local: Dictionary containing required local keys & values used to assign the profile, defaults to {}.
        :type local: dict, optional
        """
        if not isinstance(name, str):
            raise ParameterError(
                f"Invalid value for name - must be of type str, found {type(name)}"
            )
        if policy_type is not None and not isinstance(type, str):
            raise ParameterError(
                f"Invalid value for type - must be of type str, found {type(policy_type)}"
            )
        if description is not None and not isinstance(description, str):
            raise ParameterError(
                f"Invalid value for description - must be of type str, found {type(description)}"
            )
        if association is not None and not isinstance(association, str):
            raise ParameterError(
                f"Invalid value for association - must be of type str, found {type(association)}"
            )
        if security_policy is not None and not isinstance(
            security_policy, dict
        ):
            raise ParameterError(
                f"Invalid value for security_policy - must be of type dict, found {type(security_policy)}"
            )

        self.name = name
        self.type = type
        self.description = description
        self.association = association
        self.security_policy = security_policy

        if not config_dict:
            config_dict = {
                "name": name,
                "type": type,
                "description": description,
                "association": association,
                "security-policy": security_policy,
            }
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
            "POLICY", str(self.name)
        )
        self.resource = RESOURCE
        self.object_data["bulk_key"] = BULK_KEY

        if not central_conn:
            exit(
                "Unable to fetch Policy Profile without central connection. Please pass a central connection."
            )

        # Attribute used to know if object exists within Central or not
        self.materialized = False
        # Attribute used to know if object was changed recently
        self.__modified = False

    def create(self):
        """
        Perform a POST call to create a Policy Profile.

        :return: True if Policy profile was created.
        :rtype: bool
        """
        if not self.name:
            raise VerificationError(
                "Missing self.name attribute", "create() failed"
            )

        return super().create()

    def update(self):
        """
        Perform a POST call to apply changes to an existing Policy Profile.
        Source of truth is self. Perform a POST call to apply difference
        found in self to an existing Policy Profile.

        :return: True if Object was modified and a POST request was successful.
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

        :param name: Name of policy profile
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

        :param description: Description of policy profile
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

    def set_policy_type(self, policy_type):
        """
        Sets the policy type

        :param policy_type: Type of policy (e.g., "POLICY_TYPE_SECURITY")
        :type policy_type: str
        :return: None
        :raises ParameterError: If policy_type is not of type str
        """
        if not isinstance(policy_type, str):
            err_str = (
                f"invalid value for policy_type - must be of type str "
                f"- found {type(policy_type)}"
            )
            raise ParameterError(err_str)
        self.policy_type = policy_type
        self.config_dict["type"] = policy_type

    def set_association(self, association):
        """
        Sets the policy association

        :param association: Association type (e.g., "ASSOCIATION_ROLE")
        :type association: str
        :return: None
        :raises ParameterError: If association is not of type str
        """
        if not isinstance(association, str):
            err_str = (
                f"invalid value for association - must be of type str "
                f"- found {type(association)}"
            )
            raise ParameterError(err_str)
        self.association = association
        self.config_dict["association"] = association

    def get_resource_str(self):
        """
        Returns the resource string for the Policy profile.

        :return: String representation of the resource path.
        :rtype: str
        """
        return f"{self.resource}/{self.name}"

    @staticmethod
    def get_resource():
        """
        Returns the resource type for Policy profiles.

        :return: Resource type.
        :rtype: str
        """
        return RESOURCE

    @staticmethod
    def create_policy(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Create a policy using the provided parameters.

        :param central_conn: established Central connection object
        :type central_conn: ArubaCentralNewBase
        :param config_dict: Dictionary containing API keys & values used to configure the policy, defaults to {}.
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if Policy was created successfully, False otherwise.
        :rtype: bool
        """
        config_dict = config_dict.copy()

        return Profiles.create_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("POLICY"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def get_policy(name, central_conn, local={}):
        """
        GET a Policy using the provided parameters.

        :param name: name of the policy profile
        :type name: str
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: dict of Policy if present, None otherwise.
        :rtype: dict
        """
        # Validate parameters
        if not isinstance(name, str):
            raise ParameterError(
                f"Invalid value for name - must be of type str, found {type(name)}"
            )

        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("POLICY", name),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_policy(
        central_conn,
        config_dict={},
        local={},
    ):
        """
        Update a Policy using the provided parameters.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param config_dict: dictionary containing API keys & values used to
        configure the policy profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if policy was updated successfully, False otherwise.
        :rtype: bool
        """
        config_dict = config_dict.copy()

        return Profiles.update_profile(
            bulk_key=BULK_KEY,
            path=profile_utils.fetch_profile_url("POLICY"),
            central_conn=central_conn,
            config_dict=config_dict,
            local=local,
        )

    @staticmethod
    def delete_policy(name, central_conn, local={}):
        """
        Delete a Policy using the provided parameters.

        :param name: Policy name to delete
        :type name: str
        :param central_conn: established Central connection object
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If any parameter is of invalid type.
        :return: True if policy was deleted successfully, False otherwise
        :rtype: bool
        """
        # Validate parameters
        if not isinstance(name, str):
            raise ParameterError(
                f"Invalid value for name - must be of type str, found {type(name)}"
            )

        result = Profiles.delete_profile(
            path=profile_utils.fetch_profile_url("POLICY", name),
            central_conn=central_conn,
            local=local,
        )

        return result

    @staticmethod
    def create_policies(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Create multiple Policy profiles in a single API call using a POST
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param list_dict: List of Policy profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of Policy objects containing the config_dict attribute, defaults to None.
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
            path=profile_utils.fetch_profile_url("POLICY"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def get_policies(central_conn, local={}):
        """
        GET all Policies using the provided parameters.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional
        :return: dict of Policies if present, None otherwise.
        :rtype: dict
        """
        return Profiles.get_profile(
            path=profile_utils.fetch_profile_url("POLICY"),
            central_conn=central_conn,
            local=local,
        )

    @staticmethod
    def update_policies(central_conn, list_dict=None, list_obj=None, local={}):
        """
        Update multiple Policy profiles in a single API call using a PATCH
        request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param list_dict: List of profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of Policy objects containing the config_dict attribute, defaults to None.
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
            path=profile_utils.fetch_profile_url("POLICY"),
            central_conn=central_conn,
            list_dict=list_dict,
            list_obj=list_obj,
            local=local,
        )
        return result

    @staticmethod
    def delete_policies(
        central_conn, list_policy_names=None, list_policy_obj=None, local={}
    ):
        """
        Delete multiple Policy profiles through multiple API calls using
        a DELETE request.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param list_policy_names: List of Policy names to be deleted, defaults to None.
        :type list_policy_names: list, required if list_policy_obj is not provided
        :param list_policy_obj: List of Policy objects containing the object_data attribute, defaults to None.
        :type list_policy_obj: list, optional required if list_policy_names is not provided
        :param local: dictionary containing required local keys & values used
        to remove the profile, ex) {"scope_id": 12345, "persona": "GATEWAY"}
        :type local: dict, optional

        :raises ParameterError: If neither list_policy_names nor list_policy_obj is provided.
        :return: Empty if profiles were successfully deleted, populated otherwise.
        :rtype: list
        """
        path_list = []
        if not list_policy_names and not list_policy_obj:
            err_str = (
                "either list_policy_names or list_policy_obj must be provided"
            )
            raise ParameterError(err_str)

        if list_policy_names:
            for item in list_policy_names:
                if not isinstance(item, str):
                    err_str = f"Invalid value in list_policy_names - all items must be of type str, found {type(item)}"
                    raise ParameterError(err_str)
                else:
                    path_list.append(
                        profile_utils.fetch_profile_url("POLICY", item)
                    )

        elif list_policy_obj:
            for profile in list_policy_obj:
                if not isinstance(profile, Policy):
                    err_str = f"Invalid value in list_policy_obj - all items must be of type Policy, found {type(profile)}"
                    raise ParameterError(err_str)

                path_list.append(profile.object_data["path"])

        return Profiles.delete_profiles(
            path_list=path_list, central_conn=central_conn, local=local
        )

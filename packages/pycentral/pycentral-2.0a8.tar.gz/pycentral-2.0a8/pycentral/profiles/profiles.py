# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.exceptions import ParameterError
from pycentral.utils import profile_utils
from pycentral import NewCentralBase
from copy import deepcopy


class Profiles:
    def __init__(
        self, name, resource, central_conn=None, config_dict=None, local=None
    ):
        """
        instantiate a configuration Profile object

        :param name: name of the profile
        :type name: str
        :param resource: resource type for profiles - valid values found in
            pycentral.utils.profile_utils.ProfilesUtils
        :type resource: str
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :param config_dict: dictionary containing API keys & values used to
        configure the VLAN profile, defaults to {}
        :type config_dict: dict, optional
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        """
        # name and resource are required for profile assignment to a scope
        self.name = name
        self.resource = resource
        # Initialize attrs that will be later defined by child
        self.config_dict = config_dict
        self.object_data = dict()

        # Default bulk profile key is set to 'profile' but can be overridden
        self.object_data["bulk_key"] = "profile"

        self.__modified = False
        self.materialized = False

        if central_conn:
            self.central_conn = central_conn
        else:
            logger = NewCentralBase.set_logger(NewCentralBase, "INFO")
            logger.warning(
                "No Central connection provided - set central_conn before making API calls"
            )

        if local and profile_utils.validate_local(local):
            # Sample Local Data {"scope_id": 12345, "persona": "CAMPUS_AP"}
            self.local = profile_utils.validate_local(local)
        elif local:
            err_info = ", ".join(["scope_id", "persona"])
            err_str = f"Missing required local profile attributes. Please\
                provide both these values - {err_info} for the local\
                attribute."
            raise ParameterError(err_str)
        else:
            self.local = local

    def get_resource_str(self):
        return f"{self.resource}/{self.name}"

    def set_central_conn(self, central_conn):
        """
        Set the central connection object for the profile

        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, required
        """

        if not central_conn:
            raise ParameterError(
                "Central connection object not provided. Please provide a valid Central connection object"
            )

        self.central_conn = central_conn

    def get_central_conn(self):
        """
        Retrieve the Central connection object associated with the profile, if set.

        :return: The Central connection object if set, otherwise `None`.
        :rtype: NewCentralBase or None
        """

        if not hasattr(self, "central_conn") or not self.central_conn:
            self.central_conn.logger.warning(
                "No Central connection provided - set central_conn before making API calls"
            )
            return None

        return self.central_conn

    def sync_config_dict(self):
        """
        Takes attributes stored within self and if they are present as keys within
        self.config_dict then self.config_dict will be updated to match the value
        of the attribute

        :return: True or False depending if the config_dict was updated
        :rtype: bool
        """

        attr_data_dict = self.__dict__.copy()

        updated = False

        for key in attr_data_dict.keys():
            if key in self.config_dict.keys() and (
                not key.startswith("_") or not key.startswith("__")
            ):
                self.config_dict[key] = getattr(self, key)
                updated = True

        return updated

    def sync_attributes(self):
        """
        Takes keys found in self.config_dict and if they are present as attributes within
        self then self.attribute will be updated to match the value
        of that in self.config_dict[attribute]

        :return: True or False depending if the self was updated
        :rtype: bool
        """

        config_data_dict = self.config_dict.copy()

        updated = False

        for key in config_data_dict.keys():
            if key in self.__dict__.keys() and (
                not key.startswith("_") or not key.startswith("__")
            ):
                self.__dict__[key] = self.config_dict[key]
                updated = True

        return updated

    def set_config(self, config_key, config_value):
        """
        Updates self.config_dict[config_key] with the provided config_value and
        sets the attribute of the object to match the same config_value

        :param config_key: _description_
        :type config_key: _type_
        :param config_value: _description_
        :type config_value: _type_
        """
        if not config_key and isinstance(config_key) is not str:
            raise ParameterError(
                "config_key must be a valid string containing the key to update"
            )
        self.config_dict[config_key] = config_value
        self.__dict__[config_key] = config_value

    def _local_parameters(self):
        """
        Returns a dictionary of required keys/values to be used in API calls
        for local profiles. If local profile is not set, returns None.

        :return: local_attributes dictionary if self.local is set, else None
        :rtype: dict
        """
        local_attributes = None
        if self.local and profile_utils.validate_local(self.local):
            local_attributes = {"object_type": "LOCAL"}
            local_attributes.update(self.local)
        return local_attributes

    def _getattrsdict(self, config_attrs):
        """
        Utility function to dynamically retrieve attributes of an object based on
        the provided dictionary.

        :param config_attrs: dict whose keys will be the attributes to retrieve
            from the provided object with the value set to the value found in
            self, else the value in dict if not present in self.
        :type config_attrs: dict
        """
        attr_data_dict = dict()
        for key, value in config_attrs.items():
            key_underscored = key.replace("-", "_")
            if hasattr(self, key):
                attr_data_dict[key] = getattr(self, key)
            elif hasattr(self, key_underscored):
                attr_data_dict[key] = getattr(self, key_underscored)
            else:
                attr_data_dict[key] = value

        return attr_data_dict

    def _createattrs(obj, data_dictionary):
        """
        Given a dictionary object creates class attributes. The methods
            implements setattr() which sets the value of the specified
            attribute of the specified object. If the attribute is already
            created within the object. It's state changes only if the current
            value is not None. Otherwise it keeps the previous value.
        :param obj: Object instance to create/set attributes
        :type obj: PYCENTRAL object
        :param data_dictionary: dictionary containing keys that will be attrs
        :type data_dictionary: dict
        """

        # Used to create a deep copy of the dictionary
        dictionary_var = deepcopy(data_dictionary)

        # K is the argument and V is the value of the given argument
        for k, v in dictionary_var.items():
            # In case a key has '-' inside it's name.
            k = k.replace("-", "_")

            obj.__dict__[k] = v

    def create(self):
        result = False
        body = self.config_dict

        params = self._local_parameters()
        resource = self.resource
        name = self.name
        path = self.object_data["path"]

        if not hasattr(self, "central_conn") or not self.central_conn:
            raise ParameterError(
                "Create failed - Central connection required but missing in Profile. "
                "Please provide a valid Central connection object"
            )

        resp = self.central_conn.command(
            "POST", path, api_data=body, api_params=params
        )
        if resp["code"] == 200:
            self.materialized = True
            result = True
            self.central_conn.logger.info(
                f"{resource} {name} " "successfully created!"
            )
        else:
            error = resp["msg"]
            err_str = f"Error-message -> {error}"
            self.central_conn.logger.error(
                f"Failed to create {resource} {name}. {err_str}"
            )

        return result

    def get(self):
        """
        Get existing Profile from Central.

        :return: dict of Profile if present, None otherwise.
        :rtype: dict
        """
        # This GET path logic may not be the same for everything?
        path = self.object_data["path"]
        params = self._local_parameters()

        # Need to include `view_type` for GET requests
        if params:
            params.update({"view_type": "LOCAL"})

        if not hasattr(self, "central_conn") or not self.central_conn:
            raise ParameterError(
                "Get failed - Central connection required but missing in Profile. "
                "Please provide a valid Central connection object"
            )

        resp = self.central_conn.command("GET", path, api_params=params)
        return resp["msg"]

    def update(self, update_data=None):
        """
        Updates profile with values from update_data if provided. If no
        update_data provided the function will check for a diff from the
        Central profile. If a diff is found object config will be pushed to
        Central. Invalid configurations in update_data results in a failed
        update.

        :param update_data: values for updating existing profile
        :type update_data: dict
        :return result: result of profile update successful and modified
        :rtype: bool
        """
        result = False
        found_diff = False
        params = None
        body = None
        path = self.object_data["path"]
        # new_config = dict(self.config_dict)
        new_config = self.config_dict
        if update_data:
            new_config.update(update_data)

        # Check for Central profile
        central_obj = self.get()
        if central_obj:
            central_obj = central_obj
        else:
            self.materialized = False
            self.central_conn.logger.error(
                f"{self.resource} profile {self.name} not materialized. "
                "Please create profile before updating"
            )
            return result

        # Check for local/central config diff
        for key in new_config.keys():
            if key not in central_obj:
                found_diff = True
                break
        for key in central_obj.keys():
            if (
                key in new_config.keys()
                and central_obj[key] != new_config[key]
            ):
                found_diff = True
                break

        # Update profile if diff found
        if found_diff:
            self.central_conn.logger.info(
                f"Difference found between local {self.get_resource_str()} and "
                "profile found in Central. Updating profile..."
            )
            params = self._local_parameters()
            body = new_config

            # central_conn should be validated in previous self.get() but just in case
            if not hasattr(self, "central_conn") or not self.central_conn:
                raise ParameterError(
                    "Update failed - Central connection required but missing in Profile. "
                    "Please provide a valid Central connection object"
                )

            resp = self.central_conn.command(
                "POST", path, api_data=body, api_params=params
            )

            if resp["code"] == 200:
                self.central_conn.logger.info(
                    f"Successfully updated {self.get_resource_str()}!"
                )
                self._modified = True
                result = True
                # update object with with new config
                new_config = self.get()
                self.config = new_config
            else:
                result = False
                error = resp["msg"]
                err_str = f"Error-message -> {error}"
                self.central_conn.logger.error(
                    f"Failed to update {self.get_resource_str()}. {err_str}!"
                )
        else:
            self.central_conn.logger.info(
                f"No difference found between local {self.get_resource_str()} and "
                "profile found in Central. No action required."
            )
        return result

    def delete(self):
        """
        Delete profile from Central.

        :return result: result of profile delete attempt
        :rtype: bool
        """
        path = self.object_data["path"]
        params = self._local_parameters()

        resp = self.central_conn.command(
            "DELETE", path, api_params=params, headers={"Accept": "*/*"}
        )
        if resp["code"] == 200:
            self.central_conn.logger.info(
                f"{self.get_resource_str()} successfully deleted!"
            )
            return True
        else:
            self.central_conn.logger.error(
                f"Failed to delete {self.get_resource_str()}!"
            )
            return False

    @staticmethod
    def create_profile(bulk_key, path, config_dict, central_conn, local=None):
        """
        Create a configuration profile using a POST request

        :param bulk_key: The API key required for multiple profiles - valid values found in
            pycentral.utils.profile_utils.ProfilesUtils
        :type bulk_key: str
        :param path: The API path for request - valid values found in
            pycentral.utils.url_utils.NewCentralURLs
        :type path: str
        :param config_dict: dictionary containing API keys & values used to
        create the configuration profile
        :type config_dict: dict
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :param local: dictionary containing local keys & values used to assign
            the profile, defaults to {}
        :type local: dict, optional
        :raises ParameterError: If neither list_dict nor list_obj is provided.
        :return: True if profiles were successfully created, False otherwise.
        :rtype: bool
        """

        if not isinstance(config_dict, dict) or not config_dict:
            err_str = "config_dict should be a valid dictionary containing API\
                 keys & values"
            raise ParameterError(err_str)

        body = dict()
        if bulk_key is None:
            body = config_dict
        else:
            body[bulk_key] = [config_dict]

        result = False

        # defaults to None if local is not provided
        params = profile_utils.validate_local(local)

        resp = central_conn.command(
            "POST", path, api_data=body, api_params=params
        )
        if resp["code"] == 200:
            result = True
            central_conn.logger.info(
                f"{bulk_key} profile " "successfully created!"
            )
        else:
            error = resp["msg"]
            err_str = f"Error-message -> {error}"
            central_conn.logger.error(
                f"Failed to create {bulk_key} profile - {err_str}"
            )

        return result

    @staticmethod
    def get_profile(path, central_conn, local=None):
        """
        Get existing Profile from Aruba Central.

        :param path: The API path for request - valid values found in
            pycentral.utils.url_utils.NewCentralURLs
        :type path: str
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :param local: dictionary containing local keys & values used to assign
            the profile, defaults to {}
        :type local: dict, optional
        :return: dict of Profile if present, None otherwise.
        :rtype: dict
        """
        # defaults to None if local is not provided
        params = profile_utils.validate_local(local)

        # Need to include `view_type` for GET requests
        if params:
            params.update({"view_type": "LOCAL"})

        resp = central_conn.command("GET", path, api_params=params)

        return resp["msg"]

    @staticmethod
    def update_profile(bulk_key, path, config_dict, central_conn, local=None):
        """
        Create a configuration profile using a PATCH request

        :param bulk_key: The API key required for multiple profiles - valid values found in
            pycentral.utils.profile_utils.ProfilesUtils
        :type bulk_key: str
        :param path: The API path for request - valid values found in
            pycentral.utils.url_utils.NewCentralURLs
        :type path: str
        :param config_dict: dictionary containing API keys & values used to
        update the configuration profile
        :type config_dict: dict
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :param local: dictionary containing local keys & values used to assign
            the profile, defaults to {}
        :type local: dict, optional
        :raises ParameterError: If neither list_dict nor list_obj is provided.
        :return: True if profiles were successfully created, False otherwise.
        :rtype: bool
        """

        if not isinstance(config_dict, dict) or not config_dict:
            err_str = "config_dict should be a valid dictionary containing API\
                 keys & values"
            raise ParameterError(err_str)

        body = dict()
        if bulk_key is None:
            body = config_dict
        else:
            body[bulk_key] = [config_dict]

        result = False

        # defaults to None if local is not provided
        params = params = profile_utils.validate_local(local)

        resp = central_conn.command(
            "PATCH", path, api_data=body, api_params=params
        )
        if resp["code"] == 200:
            result = True
            central_conn.logger.info(
                f"{bulk_key} profile " "successfully updated!"
            )
        else:
            error = resp["msg"]
            err_str = f"Error-message -> {error}"
            central_conn.logger.error(
                f"Failed to update {bulk_key} profile - {err_str}"
            )

        return result

    @staticmethod
    def delete_profile(path, central_conn, local=None):
        """
        Delete a configuration profile using a DELETE request

        :param path: The API path of config profile to delete - valid values found in
            pycentral.utils.url_utils.NewCentralURLs
        :type path: str
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :param local: dictionary containing local keys & values used to assign
            the profile, defaults to {}
        :type local: dict, optional
        :return: True if profiles were successfully created, False otherwise.
        :rtype: bool
        """

        if not isinstance(path, str):
            err_str = "path should be a valid string containing API URL"
            raise ParameterError(err_str)

        result = False

        # defaults to None if local is not provided
        params = profile_utils.validate_local(local)

        path_split = path.split("/")
        resource = path_split[len(path_split) - 2]

        resp = central_conn.command(
            "DELETE", path, api_params=params, headers={"Accept": "*/*"}
        )

        if resp["code"] == 200:
            result = True
            central_conn.logger.info(
                f"{resource} profile " "successfully deleted!"
            )
        else:
            error = resp["msg"]
            err_str = f"Error-message -> {error}"
            central_conn.logger.error(err_str)

        return result

    @staticmethod
    def create_profiles(
        bulk_key, path, central_conn, list_dict=None, list_obj=None, local=None
    ):
        """
        Create multiple configuration profiles in a single API call using a POST
        request.

        :param bulk_key: The API key required for multiple profiles - valid values found in
            pycentral.utils.profile_utils.ProfilesUtils
        :type bulk_key: str
        :param path: The API path for request.
        :type path: str
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :param list_dict: List of profile configuration dictionaries, defaults to None.
        :type list_dict: list, required if list_obj is not provided
        :param list_obj: List of Profiles objects containing the config_dict attribute, defaults to None.
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

        body = dict()

        # Process lists and create body for bulk profile create
        if list_obj and isinstance(list_obj, list):
            body[bulk_key] = [obj.config_dict for obj in list_obj]
        elif list_dict and isinstance(list_dict, list):
            body[bulk_key] = list_dict
        else:
            err_str = "either list_dict or list_obj is invalid"
            raise ParameterError(err_str)

        result = False

        # defaults to None if local is not provided
        params = profile_utils.validate_local(local)

        resp = central_conn.command(
            "POST", path, api_data=body, api_params=params
        )
        if resp["code"] == 200:
            result = True
            central_conn.logger.info(
                f"{bulk_key} profiles " "successfully created!"
            )
        else:
            error = resp["msg"]
            err_str = f"Error-message -> {error}"
            central_conn.logger.error(
                f"Failed to create {bulk_key} profiles - {err_str}"
            )

        return result

    @staticmethod
    def update_profiles(
        bulk_key, path, central_conn, list_dict=None, list_obj=None, local=None
    ):
        """
        Update multiple configuration profiles in a single API call using a PATCH
        request.

        :param bulk_key: bulk key for profiles - valid values found in
            pycentral.utils.profile_utils.ProfilesUtils
        :type bulk_key: str
        :param path: API path for request.
        :type path: str
        :param central_conn: established Central connection object
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

        body = dict()

        # Process lists and create body for bulk create
        if list_obj:
            body[bulk_key] = [obj.config_dict for obj in list_obj]
        elif list_dict:
            body[bulk_key] = list_dict

        result = False

        # defaults to None if local is not provided
        params = profile_utils.validate_local(local)

        resp = central_conn.command(
            "PATCH", path, api_data=body, api_params=params
        )
        if resp["code"] == 200:
            result = True
            central_conn.logger.info(
                f"{bulk_key} profiles " "successfully updated!"
            )
        else:
            error = resp["msg"]
            err_str = f"Error-message -> {error}"
            central_conn.logger.error(
                f"Failed to update {bulk_key} . {err_str}"
            )

        return result

    @staticmethod
    def delete_profiles(
        path_list, central_conn, local=None, error_on_fail=True
    ):
        """
        Delete multiple configuration profiles through multiple API calls using
        a DELETE request.

        :param path_list: list of API paths as type string for requests.
        :type path_list: list, required
        :param central_conn: established Central connection object
        :type central_conn: class:`NewCentralBase`, optional
        :raises ParameterError: If neither list_dict nor list_obj is provided.
        :param local: dictionary containing required local keys & values used
        to assign the profile, ex) {"scope_id": 12345, "persona": "CAMPUS_AP"}
        :type local: dict, optional
        :param error_on_fail: list of API paths as type string for requests.
        :type error_on_fail: bool, optional
        :return: Empty if profiles were successfully deleted, populated otherwise.
        :rtype: list
        """
        if not isinstance(path_list, list) or not path_list:
            err_str = "path_list should be a valid list containing config\
                  profile URLs to be deleted"
            raise ParameterError(err_str)

        failures = []

        # defaults to None if local is not provided
        params = profile_utils.validate_local(local)

        for path in path_list:
            path_split = path.split("/")
            resource = path_split[len(path_split) - 2]
            resp = central_conn.command(
                "DELETE", path, api_params=params, headers={"Accept": "*/*"}
            )
            if resp["code"] == 200:
                central_conn.logger.info(f"{resource} successfully deleted!")
            elif error_on_fail:
                error = resp["msg"]
                err_str = f"Error-message -> {error}"
                central_conn.logger.error(
                    f"Failed to delete {resource} . {err_str}"
                )
            else:
                failures.append(path)

        return failures

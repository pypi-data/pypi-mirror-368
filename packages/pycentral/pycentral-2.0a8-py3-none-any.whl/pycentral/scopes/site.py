# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_base import ScopeBase
from ..utils import NewCentralURLs
from .scope_maps import ScopeMaps
import pytz
from datetime import datetime
from ..utils.scope_utils import (
    fetch_attribute,
    update_attribute,
    set_attributes,
    get_scope_element,
    rename_keys,
)

urls = NewCentralURLs()
scope_maps = ScopeMaps()

API_ATTRIBUTE_MAPPING = {
    "id": "id",
    "scopeName": "name",
    "address": "address",
    "city": "city",
    "state": "state",
    "country": "country",
    "zipcode": "zipcode",
    "longitude": "longitude",
    "latitude": "latitude",
    "collectionName": "site_collection_name",
    "collectionId": "site_collection_id",
    "deviceCount": "associated_devices",
    "timezone": "timezone",
    "image": "image",
}

REQUIRED_ATTRIBUTES = [
    "name",
    "address",
    "city",
    "state",
    "country",
    "zipcode",
    "timezone",
]

OPTIONAL_ATTRIBUTES = {
    "id": None,
    "latitude": None,
    "longitude": None,
    "image": {"name": "", "contentType": ""},
    "associated_devices": 0,
    "devices": [],
    "site_collection_name": None,
    "site_collection_id": None,
    "assigned_profiles": [],
}


class Site(ScopeBase):
    """
    This class holds site and all of its attributes & related methods.
    """

    def __init__(self, site_attributes, central_conn=None, from_api=False):
        """
        Constructor for Site object

        :param site_attributes: Attributes of the site collection
        :type site_attributes: dict
        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param from_api: Boolean indicates if the site_attributes is from the Central API response.
        :type from_api: bool, optional
        """
        if from_api:
            site_attributes = rename_keys(
                site_attributes, API_ATTRIBUTE_MAPPING
            )

        self.materialized = from_api
        self.central_conn = central_conn
        self.id = None
        self.type = "site"

        missing_required_attributes = [
            attr for attr in REQUIRED_ATTRIBUTES if attr not in site_attributes
        ]
        if missing_required_attributes:
            raise ValueError(
                f'Missing required attributes: {", ".join(missing_required_attributes)}'
            )
        valid_attributes = REQUIRED_ATTRIBUTES + list(
            OPTIONAL_ATTRIBUTES.keys()
        )
        unexpected_attributes = [
            attr for attr in site_attributes if attr not in valid_attributes
        ]
        if unexpected_attributes:
            raise ValueError(
                f'Unexpected attributes: {", ".join(unexpected_attributes)}.\n If site is being created based off api_response ensure that the from_api flag is set to True'
            )
        set_attributes(
            obj=self,
            attributes_dict=site_attributes,
            required_attributes=REQUIRED_ATTRIBUTES,
            optional_attributes=OPTIONAL_ATTRIBUTES,
        )

    def create(self):
        """
        Perform a POST call to create a site on Central.

        :return: True if site was created, else False
        :rtype: bool
        """
        if self.materialized:
            raise Exception("Unable to create a site that already exists")

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_creation_status = False
        api_method = "POST"
        api_path = urls.fetch_url("SCOPES", "SITE")
        api_data = self.__generate_api_body()

        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_data=api_data
        )
        if resp["code"] == 200:
            try:
                site_id = resp["msg"]["items"][0]
                self.id = int(site_id)
                self.materialized = True
                site_creation_status = True
                self.get()
                self.central_conn.logger.info(
                    f"Successfully created site {self.get_name()} in Central"
                )
            except KeyError:
                self.central_conn.logger.info(
                    f"Failed to set site id of site {self.get_name()}"
                )
                pass
        else:
            self.central_conn.logger.error(
                f'Failed to create site {self.get_name()} in Central.\nError message - {resp["msg"]}'
            )
        return site_creation_status

    def get(self):
        """
        Performs a GET call to retrieve data of a site then sets attributes of self based on API response.

        :return: Returns JSON Data of GET call if success, else None
        :rtype: dict
        """
        if not self.materialized:
            raise Exception("Unable to get a site that does not exist")

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_data = get_scope_element(
            obj=self, scope="site", scope_id=self.get_id()
        )
        if not site_data:
            self.materialized = False
            self.central_conn.logger.error(
                f"Unable to fetch site {self.get_name()} from Central"
            )
        else:
            site_attributes = rename_keys(site_data, API_ATTRIBUTE_MAPPING)
            set_attributes(
                obj=self,
                attributes_dict=site_attributes,
                required_attributes=REQUIRED_ATTRIBUTES,
                optional_attributes=OPTIONAL_ATTRIBUTES,
            )
            self.central_conn.logger.info(
                f"Successfully fetched site {self.get_name()} from Central."
            )
        return site_data

    def update(self):
        """
        Performs a PUT call to update attributes of site on Central if any changes are detected. The source of truth is self

        :return: Returns JSON Data of GET call if success, else None
        :rtype: dict
        """
        if not self.materialized:
            raise Exception(
                "Unable to update a site that does not exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        modified = False
        site_data = get_scope_element(
            obj=self, scope="site", scope_id=self.get_id()
        )

        if not site_data:
            self.materialized = False
            raise Exception(
                "Unable to upate site as it could not be found in Central."
            )

        site_attributes = rename_keys(site_data, API_ATTRIBUTE_MAPPING)

        object_attributes = {
            key: getattr(self, key) for key in API_ATTRIBUTE_MAPPING.values()
        }

        if site_attributes != object_attributes:
            api_method = "PUT"
            api_path = urls.fetch_url("SCOPES", "SITE")
            api_data = self.__generate_api_body()

            resp = self.central_conn.command(
                api_method=api_method, api_path=api_path, api_data=api_data
            )
            if resp["code"] == 200:
                modified = True
                self.central_conn.logger.info(
                    f"Successfully updated site {self.get_name()} in Central"
                )
            else:
                self.central_conn.logger.info(
                    f"Failed to update site {self.get_name()} in Central.\n Error message - {resp['msg']}"
                )
        return modified

    def delete(self):
        """
        Performs DELETE call to delete Site.

        :return: True if DELETE was successful, else returns False if DELETE was unsuccessful
        :rtype: bool
        """
        if not self.materialized:
            raise Exception(
                "Unable to delete a site that doesn't exist on Central"
            )

        if self.central_conn is None:
            raise Exception(
                "Unable to create site without Central connection. Please provide the central connection with the central_conn variable."
            )

        site_deletion_status = False
        api_method = "DELETE"
        api_path = urls.fetch_url("SCOPES", "SITE")
        api_params = {"scopeId": self.get_id()}
        resp = self.central_conn.command(
            api_method=api_method, api_path=api_path, api_params=api_params
        )
        if resp["code"] == 200:
            self.id = None
            self.materialized = False
            site_deletion_status = True
            self.central_conn.logger.info(
                f"Successfully deleted site {self.get_name()}"
            )

        else:
            self.central_conn.logger.error(
                f"Failed to delete site {self.get_name()}.\n Error message - {resp['msg']}"
            )
        return site_deletion_status

    def get_site_collection_attributes(self):
        """
        returns dictionary of site collection attributes of the site if site collection id
            is defined or None if not

        :return: dictionary of site collection attributes or None
        :rtype: dict
        """
        if fetch_attribute(self, "site_collection_id"):
            return {
                "id": fetch_attribute(self, "site_collection_id"),
                "name": fetch_attribute(self, "site_collection_name"),
            }
        return None

    def add_site_collection(self, site_collection_id, site_collection_name):
        """
        This function sets the attributes site collection id and name of this site object

        :param site_collection_id: site collection id
        :type site_collection_id: str
        :param site_collection_name: site collection name
        :type site_collection_name: str
        """
        update_attribute(
            self, attribute="site_collection_id", new_value=site_collection_id
        )

        update_attribute(
            self,
            attribute="site_collection_name",
            new_value=site_collection_name,
        )

    def remove_site_collection(self):
        """
        sets the attributes of site collection id and name this site object
            belongs to None
        """

        update_attribute(self, attribute="site_collection_id", new_value=None)
        update_attribute(
            self, attribute="site_collection_name", new_value=None
        )

    def __str__(self):
        """
        String containing the Site id and name
        :return: This class' string representation.
        :rtype: str
        """
        return f"Site ID - {self.get_id()}, Site Name - {self.get_name()}"

    def __generate_api_body(self):
        """
        This function returns the dictionary of site attributes are needed to making API calls

        :return: Dictionary of site attributes needed for making API calls to Central.
        :rtype: dict
        """
        api_body = {
            "name": self.get_name(),
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zipcode": self.zipcode,
            "timezone": self.__get_timezone_attributes(),
        }
        if self.materialized:
            api_body["scopeId"] = str(self.get_id())
            optional_attributes = list(
                set(API_ATTRIBUTE_MAPPING.values())
                - set(api_body.keys())
                - set(["id"])
            )
            for key in optional_attributes:
                if hasattr(self, key):
                    api_key = next(
                        (
                            k
                            for k, v in API_ATTRIBUTE_MAPPING.items()
                            if v == key
                        ),
                        None,
                    )
                    if api_key:
                        api_body[api_key] = getattr(self, key)

        return api_body

    def __get_timezone_attributes(self):
        """
        This function returns the dictionary of timezone attributes that are needed to making API calls

        :return: Dictionary of timezone attributes needed for making site management API calls to Central.
        :rtype: dict
        """
        timezone = pytz.timezone(self.timezone)
        current_time = datetime.now(timezone)
        raw_offset = int(current_time.utcoffset().total_seconds() * 1_000)

        return {
            "rawOffset": raw_offset,
            "timezoneId": self.timezone,
            "timezoneName": current_time.tzname(),
        }

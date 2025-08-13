# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..scopes.scope_maps import ScopeMaps
from pycentral.utils import NewCentralURLs
import copy

scope_maps = ScopeMaps()
urls = NewCentralURLs()

SUPPORTED_SCOPES = ["site", "site_collection", "device_group"]
DEFAULT_LIMIT = 100


def fetch_attribute(obj, attribute):
    """
    This function fetches the value associated with the provided attribute in the object, if it exists.

    :param obj: Object whose attribute has to be returned
    :type obj: class
    :param attribute: Attribute within the object that has to be returned
    :type attribute: str

    :return: Value of the required attribute, if it exists in the object. If the attribute doesn't exist, it will return None.
    :rtype: string
    """
    if hasattr(obj, attribute):
        return getattr(obj, attribute)
    return None


def update_attribute(obj, attribute, new_value):
    """
    This function updates the value of the provided attribute in the object, if it exists.

    :param obj: Object whose attribute has to be updated
    :type obj: class
    :param attribute: Attribute within the object that has to be updated
    :type attribute: str

    :return: True if the attribute was successfully updated, else False.
    :rtype: bool
    """
    if hasattr(obj, attribute):
        setattr(obj, attribute, new_value)
        return True
    return False


def get_attributes(obj):
    """
    This function returns all attributes of the provided class

    :param obj: Object whose attribute has to be returned
    :type obj: class

    :return: Returns attributes defined in the Site Collection object
    :rtype: dict
    """
    return {k: v for k, v in obj.__dict__.items() if not callable(v)}


def get_all_scope_elements(obj, scope):
    """
    This function makes GET API calls to Central to get all the elements of the specified scope. This method is supported for site, site collection, device & device groups scopes.

    :param obj: Class instance that will be used to make API calls to Central
    :type obj: class
    :param scope: The type of the element. SITE_COLLECTION, SITE, DEVICE, DEVICE_GROUP are valid parameters for this argument
    :type scope: str

    :return: List of all scope elements. If there are errors it will return None.
    :rtype: list
    """
    if scope not in SUPPORTED_SCOPES:
        obj.central_conn.logger.error(
            "Unknown scope provided. Please provide one of the supported scopes - "
            ", ".join(SUPPORTED_SCOPES)
        )
        return None
    limit = DEFAULT_LIMIT
    offset = 1
    scope_elements = []
    number_of_scope_elements = None
    while (
        number_of_scope_elements is None
        or len(scope_elements) < number_of_scope_elements
    ):
        resp = get_scope_elements(obj, scope, limit=limit, offset=offset)
        if resp["code"] == 200:
            offset += 1
            resp_message = resp["msg"]
            if number_of_scope_elements is None:
                number_of_scope_elements = resp_message["total"]

            scope_elements.extend(
                [scope_element for scope_element in resp_message["items"]]
            )
        else:
            obj.central_conn.logger.error(resp["msg"]["message"])
        obj.central_conn.logger.info(
            f"Total {scope}s fetched from account: {len(scope_elements)}"
        )
        return scope_elements


def get_scope_elements(
    obj, scope, limit=50, offset=0, filter_field="", sort=""
):
    """
    This function makes GET APIs to Central to get the list of scope elements based on the provided attributes. This method is supported for site, site collection, device & device groups scopes.

    :param obj: Class instance that will be used to make API calls to Central
    :type obj: class
    :param scope: The type of the element. SITE_COLLECTION, SITE, DEVICE, DEVICE_GROUP are valid parameters for this argument
    :type scope: str
    :param limit: Number of scope elements to be fetched, defaults to 50
    :type limit: int
    :param offset: Pagination start index, defaults to 1
    :type offset: int
    :param filter_field: Field that needs to be used for sorting the list of sites or site collections. Accepted values for sites is scopeName, address, state, country, city, deviceCount, collectionName, zipcode, timezone. Accepted values for this argument for site_collection is scopeName, description, deviceCount, siteCount
    :type filter_field: str, optional
    :param sort: Direction of sorting for the field. ASC or DESC are accepted values for this argument
    :type sort: str, optional

    :return: List of scope elements based on the provided arguments. If there are errors it will return None.
    :rtype: list
    """
    if scope not in SUPPORTED_SCOPES:
        obj.central_conn.logger.error(
            "Unknown scope provided. Please provide one of the supported scopes - "
            ", ".join(SUPPORTED_SCOPES)
        )
        return None

    api_path = urls.fetch_url("SCOPES", scope.upper())
    api_method = "GET"
    api_params = {"limit": limit, "offset": offset}

    if filter_field:
        api_params["filter"] = filter_field
    if sort:
        api_params["sort"] = sort

    resp = obj.central_conn.command(
        api_method=api_method, api_path=api_path, api_params=api_params
    )
    return resp


def set_attributes(
    obj,
    attributes_dict,
    required_attributes,
    optional_attributes=None,
    object_attributes=None,
):
    """
    This sets the attributes of the given object based on the attributes_dict

    :param obj: Class instance that will be used to make API calls to Central
    :type obj: class
    :param attributes_dict: Attributes that will be updated to self
    :type attributes_dict: dict
    """
    for attr in required_attributes:
        value = attributes_dict[attr]
        setattr(obj, attr, value)

    if optional_attributes:
        for attr, default_value in optional_attributes.items():
            value = attributes_dict.get(attr)
            if not value:
                if isinstance(default_value, list):
                    value = copy.deepcopy(default_value)
                else:
                    value = default_value
            setattr(obj, attr, value)
    if object_attributes:
        for attr, default_value in object_attributes.items():
            if attr in attributes_dict:
                setattr(obj, attr, attributes_dict[attr])
            else:
                setattr(obj, attr, default_value)


def get_scope_element(obj, scope, scope_id=None, serial=None):
    """
    This function makes GET APIs to Central to find the specified scope element & return that data. This method is supported for site, site collection, device & device groups scopes.

    :param obj: Class instance that will be used to make API calls to Central
    :type obj: class
    :param scope: The type of the element. SITE_COLLECTION, SITE, DEVICE, DEVICE_GROUP are valid parameters for this argument
    :type scope: str
    :param scope_id: ID of the scope element to be returned (optional)
    :type scope_id: int, optional
    :param serial: Serial number of the device to be returned (only for DEVICE scope, optional)
    :type serial: str, optional

    :return: If the site collection or device is found, the attributes associated with it are returned from Central, else None is returned
    :rtype: dict
    """
    if scope not in SUPPORTED_SCOPES:
        obj.central_conn.logger.error(
            f"Unsupported scope '{scope}'. Supported scopes are: {', '.join(SUPPORTED_SCOPES)}"
        )
        return None

    if scope == "device" and serial:
        scope_elements_list = get_all_scope_elements(obj=obj, scope=scope)
        for element in scope_elements_list:
            if element.get("scopeName") == serial:
                return element
    elif scope_id is not None:
        scope_elements_list = get_all_scope_elements(obj=obj, scope=scope)
        for element in scope_elements_list:
            if element.get("scopeId") == str(scope_id):
                return element

    return None


def rename_keys(api_dict, api_attribute_mapping):
    """
    This function renames the keys of the site attributes from the API
    response

    :param api_dict: dict of information from Central API Response
    :type api_dict: dict
    :param api_attribute_mapping: Dict of Object attributes mapped to keys
    from Central API Response
    :type api_attribute_mapping: dict

    :return: Renamed dictionary of Object attributes. The renamed keys maps
    to attributes that will be defined in the Object
    :rtype: dict
    """

    # ️ Removing reduntant keys
    extra_keys = ["type", "scopeId"]
    for key in extra_keys:
        if key in api_dict.keys():
            del api_dict[key]
    integer_attributes = ["id", "collectionId", "deviceCount"]
    renamed_dict = {}
    for key, value in api_dict.items():
        new_key = api_attribute_mapping.get(key)
        if new_key:
            if key in integer_attributes and value:
                value = int(value)
            elif key == "timezone" and "timezoneId" in value:
                value = value["timezoneId"]
            renamed_dict[new_key] = value
        else:
            raise ValueError(f"Unknown attribute {key} found in API response")
    return renamed_dict


def validate_find_scope_elements(ids=None, names=None, serials=None, scope=""):
    """
    Validates the input parameters for the _find_scope_elements method.

    :param ids: ID(s) of the element(s)
    :type ids: str or list
    :param names: Name(s) of the element(s)
    :type names: str or list
    :param serials: Serial number(s) of the element(s) (only for devices)
    :type serials: str or list
    :param scope: Specific scope to search in (e.g., "site", "device")
    :type scope: str, optional

    :raises ValueError: If validation fails
    """
    # Ensure only one of ids, names, or serials is provided
    provided_params = [ids, names, serials]
    if sum(param is not None for param in provided_params) > 1:
        raise ValueError("Provide only one of 'ids', 'names', or 'serials'.")

    # If serials are provided, ensure the scope is "device" or no scope is provided
    if serials and scope and scope.lower() != "device":
        raise ValueError(
            "Serials can only be used with the 'device' scope or when no scope is provided."
        )


def lookup_in_map(keys, lookup_map):
    """
    Helper method to perform lookup in a nested map.

    :param keys: Key(s) to look up
    :type keys: str or list
    :param lookup_map: Map to search in
    :type lookup_map: dict
    :param key_type: The type of key to use for lookup (e.g., "id", "name", "serial")
    :type key_type: str

    :return: Found value(s) or None if not found
    :rtype: dict, list, or None
    """

    if isinstance(keys, (str, int)):
        return lookup_map.get(keys)
    return [lookup_map.get(key) for key in keys if key in lookup_map]

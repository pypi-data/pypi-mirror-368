# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_base import ScopeBase
from ..utils import NewCentralURLs
from .scope_maps import ScopeMaps
from ..utils.scope_utils import fetch_attribute
from ..utils.constants import SUPPORTED_CONFIG_PERSONAS
from ..utils.troubleshooting_utils import TROUBLESHOOTING_METHOD_DEVICE_MAPPING
from ..troubleshooting import Troubleshooting

urls = NewCentralURLs()
scope_maps = ScopeMaps()

CX_API_ENDPOINT = "cx"
AOS_S_API_ENDPOINT = "aos-s"

# Device type mapping from Central API device types to troubleshooting API endpoints
DEVICE_TYPE_MAPPING = {
    "ACCESS_POINT": "aps",
    "GATEWAY": "gateways",
    "SWITCH": None,  # Requires OS identification for switches
}

# Switch OS mapping based on model prefixes
SWITCH_OS_MAPPING = {
    # AOS-CX prefixes
    "6": CX_API_ENDPOINT,  # 6xxx series
    "8": CX_API_ENDPOINT,  # 8xxx series
    "9": CX_API_ENDPOINT,  # 9xxx series
    "1": CX_API_ENDPOINT,  # 10xx series
    "4": CX_API_ENDPOINT,  # 4xxx series
    # AOS-Switch (AOS-S) prefixes
    "2": AOS_S_API_ENDPOINT,  # 2xxx series
    "3": AOS_S_API_ENDPOINT,  # 3xxx series
    "5": AOS_S_API_ENDPOINT,  # 5xxx series
}

API_ATTRIBUTE_MAPPING = {
    "scopeId": "id",
    "deviceName": "name",
    "deviceGroupName": "group_name",
    "deviceGroupId": "group_id",
    "serialNumber": "serial",
    "deployment": "deployment",
    "siteName": "site_name",
    "siteId": "site_id",
    "macAddress": "mac",
    "model": "model",
    "persona": "persona",
    "softwareVersion": "software-version",
    "role": "role",
    "partNumber": "part-number",
    "isProvisioned": "provisioned_status",
    "status": "status",
    "deviceType": "device_type",
    "ipv4": "ipv4",
    "deviceFunction": "device_function",
}

REQUIRED_ATTRIBUTES = ["name", "serial"]


class Device(ScopeBase):
    """
    This class holds device and all of its attributes & related methods.
    """

    def __init__(
        self,
        device_attributes=None,
        central_conn=None,
        serial=None,
        from_api=False,
    ):
        """
        Constructor for Device object

        :param serial: Serial number of the device (required if device_attributes is not provided).
        :type serial: str
        :param device_attributes: Attributes of the Device.
        :type device_attributes: dict
        :param central_conn: Instance of class:`pycentral.NewCentralBase`
        to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param from_api: Boolean indicates if the device_attributes is from the
        Central API response.
        :type from_api: bool, optional
        """

        # If device_attributes is provided, use it to set attributes
        self.materialized = from_api
        self.central_conn = central_conn
        self.type = "device"
        if from_api:
            # Rename keys if attributes are from API
            device_attributes = self.__rename_keys(
                device_attributes, API_ATTRIBUTE_MAPPING
            )
            device_attributes["assigned_profiles"] = []
            for key, value in device_attributes.items():
                setattr(self, key, value)
            if (
                self.provisioned_status
                and device_attributes["persona"] in SUPPORTED_CONFIG_PERSONAS
            ):
                self.config_persona = SUPPORTED_CONFIG_PERSONAS[
                    device_attributes["persona"]
                ]
        # If only serial is provided, set it and defer fetching other details
        elif serial:
            self.serial = serial

        # If neither serial nor device_attributes is provided, raise an error
        else:
            raise ValueError(
                "Either 'serial' or 'device_attributes(from api response)' must be provided to create a Device."
            )

    def get_serial(self):
        """
        returns the value of self.serial

        :return: value of self.serial
        :rtype: str
        """
        return fetch_attribute(self, "serial")

    def get(self):
        """
        Fetches the device details from the Central API using the serial number.

        :return: Device attributes as a dictionary.
        :rtype: dict
        """
        if self.central_conn is None:
            raise Exception(
                "Unable to get device without Central connection. Please provide the central connection with the central_conn variable."
            )
        device_data = Device.get_devices(
            self.central_conn,
            search=str(self.get_serial()),
            limit=1,
        )
        self.materialized = len(device_data["items"]) == 1
        if not self.materialized:
            self.materialized = False
            self.central_conn.logger.error(
                f"Unable to fetch device {self.get_serial()} from Central"
            )
        else:
            device_attributes = self.__rename_keys(
                device_data["items"][0], API_ATTRIBUTE_MAPPING
            )
            device_attributes["assigned_profiles"] = []
            for key, value in device_attributes.items():
                setattr(self, key, value)
            self.central_conn.logger.info(
                f"Successfully fetched device {self.get_serial()}'s data from Central."
            )
        return device_data

    @staticmethod
    def get_all_devices(central_conn, new_central_provisioned=False):
        """
        Fetches all devices from Central, optionally filtering for new Central configured devices.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param new_central_provisioned: If True, only devices that are provisioned via New Central are returned.
        :type new_central_provisioned: bool, optional
        :return: List of device dictionaries fetched from Central.
        :rtype: list
        """
        limit = 100
        next_cursor = 1
        device_list = []

        while True:
            device_resp = Device.get_devices(
                central_conn, limit=limit, next_cursor=next_cursor
            )
            if device_resp is None:
                central_conn.logger.error("Error fetching list of devices")
                device_list = []
                break
            device_list.extend(device_resp["items"])
            if len(device_list) == device_resp["total"]:
                central_conn.logger.info(
                    f"Total devices fetched from account: {len(device_list)}"
                )
                break
            next_cursor += 1

        if new_central_provisioned:
            new_central_device_list = [
                device
                for device in device_list
                if device.get("isProvisioned") == "Yes"
            ]
            return new_central_device_list
        return device_list

    @staticmethod
    def get_devices(
        central_conn,
        filter_string=None,
        sort=None,
        search=None,
        site_assigned=None,
        limit=20,
        next_cursor=1,
    ):
        """
        Fetch device inventory from New Central with optional filtering, sorting, and pagination.

        :param filter: Dictionary of attributes to filter devices by.
        :param sort: Sorting criteria for the device list.
        :param search: Search term to apply to device attributes. Search term to filter devices. Supported fields are: "deviceName", "persona", "model", "serialNumber", "macAddress", "ipv4", "softwareVersion"
        :param site_assigned: Specifies the site assignment status of the devices. Can be either "ASSIGNED" or "UNASSIGNED".
        :param limit: Maximum number of devices to return.
        :param next: Pagination cursor for fetching the next set of devices. Minimum is 1

        :return: List of devices matching the criteria.
        :rtype: list
        """
        # Construct API parameters with only non-None values
        api_params = {}
        if filter_string is not None:
            api_params["filter"] = filter_string
        if sort is not None:
            api_params["sort"] = sort
        if search is not None:
            api_params["search"] = search
        if site_assigned is not None:
            api_params["site-assigned"] = site_assigned
        if limit is not None:
            api_params["limit"] = limit
        if next_cursor is not None:
            api_params["next"] = next_cursor

        # Call the Central API
        resp = central_conn.command(
            api_method="GET",
            api_path="network-monitoring/v1alpha1/device-inventory",
            api_params=api_params,
        )

        if resp["code"] != 200:
            central_conn.logger.error(
                f"Error fetching devices: {resp['code']} - {resp['msg']}"
            )
            return []

        return resp["msg"]

    def __rename_keys(self, api_dict, api_attribute_mapping):
        """
        Renames the keys of the attributes from the API response.

        :param api_dict: dict from Central API Response
        :type api_dict: dict
        :param api_attribute_mapping: Dict mapping API keys to object attributes
        :type api_attribute_mapping: dict
        :return: Renamed dictionary of object attributes
        :rtype: dict
        """
        integer_attributes = {"scopeId"}
        renamed_dict = {}
        for key, value in api_dict.items():
            new_key = api_attribute_mapping.get(key)
            if not new_key:
                continue  # Skip unknown keys
            if key in integer_attributes and value is not None:
                value = int(value)
            if key == "isProvisioned":
                value = True if value == "Yes" else False
            renamed_dict[new_key] = value
        return renamed_dict

    def ping_test(self, destination, **kwargs):
        """
        Initiates a ping test to the specified destination from the device.

        :param destination: The IP address or hostname to ping.
        :type destination: str
        :param kwargs: Optional arguments specific to device type.
                      See Troubleshooting.ping_test() for detailed parameter information.
        :return: Result of the ping test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.ping_test, destination=destination, **kwargs
        )

    def traceroute_test(self, destination, **kwargs):
        """
        Initiates a traceroute test to the specified destination from the device.

        Supported device types: All (aps, cx, aos-s, gateways)

        :param destination: The IP address or hostname to traceroute.
        :type destination: str
        :param kwargs: Optional arguments specific to device type.
                      See Troubleshooting.traceroute_test() for detailed parameter information.
        :return: Result of the traceroute test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.traceroute_test, destination=destination, **kwargs
        )

    def reboot(self):
        """
        Reboots the device.

        Supported device types: All (aps, cx, aos-s, gateways)

        :return: Result of the reboot operation.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.reboot_device
        )

    def locate_test(self):
        """
        Initiates a locate test (LED blinking) on the device.

        Supported device types: cx, aps, aos-s (gateways not supported)

        :return: Result of the locate test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.locate_device
        )

    def http_test(self, destination, **kwargs):
        """
        Initiates an HTTP test to the specified destination from the device.

        Supported device types: cx, aps, gateways

        :param destination: The IP address or hostname to test.
        :type destination: str
        :param kwargs: Optional arguments specific to device type.
                      See Troubleshooting.http_test() for detailed parameter information.
        :return: Result of the HTTP test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.http_test, destination=destination, **kwargs
        )

    def https_test(self, destination, **kwargs):
        """
        Initiates an HTTPS test to the specified destination from the device.

        Supported device types: aps, gateways, cx (uses HTTP endpoint with HTTPS protocol)

        :param destination: The IP address or hostname to test.
        :type destination: str
        :param kwargs: Optional arguments specific to device type.
                      See https_cx_test(), https_aps_test(), or https_gateways_test() for detailed parameter information.
        :return: Result of the HTTPS test.
        :rtype: dict
        """
        self._ensure_materialized()

        if (
            self.device_type == "SWITCH"
            and self._identify_switch_os() == CX_API_ENDPOINT
        ):
            return Troubleshooting.https_cx_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "ACCESS_POINT":
            return Troubleshooting.https_aps_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        elif self.device_type == "GATEWAY":
            return Troubleshooting.https_gateways_test(
                central_conn=self.central_conn,
                serial_number=self.serial,
                destination=destination,
                **kwargs,
            )
        else:
            raise ValueError(
                f"HTTPS test is not supported for device type {self.device_type}."
            )

    def port_bounce_test(self, ports, **kwargs):
        """
        Initiates a port bounce test on the specified ports.

        Supported device types: cx, aos-s, gateways

        :param ports: List of ports to test.
        :type ports: list
        :return: Result of the port bounce test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.port_bounce_test, ports=ports, **kwargs
        )

    def poe_bounce_test(self, ports, **kwargs):
        """
        Initiates a PoE bounce test on the specified ports.

        Supported device types: cx, aos-s, gateways

        :param ports: List of ports to test.
        :type ports: list
        :return: Result of the PoE bounce test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.poe_bounce_test, ports=ports, **kwargs
        )

    def arp_test(self):
        """
        Initiates an ARP table retrieval test on the device.

        Supported device types: aos-s, aps, gateways

        :return: Result of the ARP test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.retrieve_arp_table_test
        )

    def speedtest_test(self, iperf_server_address, **kwargs):
        """
        Initiates a speed test using the specified iPerf server address.

        Supported device types: aps only

        :param iperf_server_address: The IP address or hostname of the iPerf server.
        :type iperf_server_address: str
        :param kwargs: Optional arguments for the speed test.
                      See Troubleshooting.speedtest_test() for detailed parameter information.
        :return: Result of the speed test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.speedtest_test,
            iperf_server_address=iperf_server_address,
            **kwargs,
        )

    def tcp_test(self, host, port, **kwargs):
        """
        Initiates a TCP test to the specified host and port from the device.

        Supported device types: aps only

        :param host: The IP address or hostname to test.
        :type host: str
        :param port: The port number to test.
        :type port: int
        :param kwargs: Optional arguments for the TCP test.
                      See Troubleshooting.tcp_test() for detailed parameter information.
        :return: Result of the TCP test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.tcp_test, host=host, port=port, **kwargs
        )

    def aaa_test(
        self, auth_method_type, radius_server_ip, username, password, **kwargs
    ):
        """
        Initiates an AAA test with the specified parameters.

        Supported device types: cx only

        :param auth_method_type: Authentication method type, chap or pap
        :type auth_method_type: str
        :param radius_server_ip: RADIUS server IP address
        :type radius_server_ip: str
        :param username: Username for authentication
        :type username: str
        :param password: Password for authentication
        :type password: str
        :param kwargs: Optional arguments for the AAA test.
                      See Troubleshooting.aaa_test() for detailed parameter information.
        :return: Result of the AAA test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.aaa_test,
            auth_method_type=auth_method_type,
            radius_server_ip=radius_server_ip,
            username=username,
            password=password,
            **kwargs,
        )

    def cable_test(self, ports, **kwargs):
        """
        Initiates a Cable test on the specified ports.

        Supported device types: cx, aos-s

        :param ports: List of ports to test.
        :type ports: list
        :return: Result of the Cable test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.cable_test, ports=ports, **kwargs
        )

    def iperf_test(self, server_address, **kwargs):
        """
        Initiates an iPerf test using the specified server address.

        Supported device types: gateways only

        :param server_address: The IP address or hostname of the iPerf server.
        :type server_address: str
        :param kwargs: Optional arguments for the iPerf test.
                      See Troubleshooting.iperf_test() for detailed parameter information.
        :return: Result of the iPerf test.
        :rtype: dict
        """
        return self._execute_troubleshooting_command(
            Troubleshooting.iperf_test,
            server_address=server_address,
            **kwargs,
        )

    def _execute_troubleshooting_command(self, command_method, **kwargs):
        """
        Executes a troubleshooting command with common setup.

        :param command_method: The troubleshooting method to call.
        :type command_method: callable
        :param kwargs: Additional arguments to pass to the command.
        :return: Result of the troubleshooting command.
        :rtype: dict
        """
        self._ensure_materialized()
        device_type = self._get_effective_device_type()

        method_name = command_method.__name__
        if (
            method_name in TROUBLESHOOTING_METHOD_DEVICE_MAPPING
            and device_type
            not in TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(method_name)
        ):
            raise ValueError(
                f"{method_name} is not supported for device type {device_type}. Supported types are: {TROUBLESHOOTING_METHOD_DEVICE_MAPPING.get(method_name)}"
            )
        return command_method(
            central_conn=self.central_conn,
            device_type=device_type,
            serial_number=self.serial,
            **kwargs,
        )

    def _ensure_materialized(self):
        """
        Ensures the device is materialized before performing operations.

        :raises Exception: If device is not materialized.
        """
        if not self.materialized:
            raise Exception(
                "Device is not materialized. Please fetch the device details first."
            )

    def _get_effective_device_type(self):
        """
        Gets the effective device type, resolving switch OS if needed.

        :return: The effective device type for troubleshooting operations.
        :rtype: str
        """
        device_type = self.device_type

        # Use mapping for direct conversions
        if device_type in DEVICE_TYPE_MAPPING:
            mapped_type = DEVICE_TYPE_MAPPING[device_type]
            if mapped_type is not None:
                return mapped_type
            elif device_type == "SWITCH":
                # Special case: switches require OS identification
                return self._identify_switch_os()

        # Fallback for unsupported device types
        raise ValueError(
            f"Unsupported device type for troubleshooting: {device_type}. "
            f"Supported types are: {', '.join([v for v in DEVICE_TYPE_MAPPING.values() if v is not None] + ['cx', 'aos-s'])}."
        )

    def _identify_switch_os(self):
        if self.device_type != "SWITCH":
            raise ValueError(
                "This method is only applicable for devices of type 'SWITCH'."
            )

        if not hasattr(self, "model") or not self.model:
            raise ValueError(
                "Device model information is required to identify switch OS."
            )

        prefix = self.model[:1]

        if prefix in SWITCH_OS_MAPPING:
            return SWITCH_OS_MAPPING[prefix]
        else:
            raise ValueError(
                f"Unable to identify switch OS for model '{self.model}'. "
                f"Supported model prefixes: {', '.join(SWITCH_OS_MAPPING.keys())}"
            )

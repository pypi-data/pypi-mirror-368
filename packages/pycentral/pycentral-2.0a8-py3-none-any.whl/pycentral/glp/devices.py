# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.url_utils import NewCentralURLs, urlJoin
from .subscriptions import Subscriptions
from ..utils.glp_utils import check_progress, rate_limit_check
import time

urls = NewCentralURLs()

DEVICE_GET_LIMIT = 2000
# Input size per request for DEVICE module APIs.
INPUT_SIZE = 5
# Rate limit for PATCH Device functions.
PATCH_RPM = 5
# Rate limit for POST Device functions.
POST_RPM = 4


class Devices(object):
    def get_all_devices(self, conn, select=None):
        """
        Get a list of devices managed in a workspace.

        :param select: A comma separated list of select properties to display in the response. The default is that all properties are returned.
        :type select: Array of strings unique (Example: select=serialNumber,macAddress)
        :return: A list of all devices in the workspace, or an empty list if an error occurs.
        :rtype: list of dict
        """
        conn.logger.info("Getting all devices in GLP workspace")
        limit = DEVICE_GET_LIMIT
        offset = 0
        device_list = []

        while True:
            resp = self.get_device(
                conn, limit=limit, offset=offset, select=select
            )
            if resp["code"] != 200:
                conn.logger.error(
                    f"Error fetching list of devices: {resp['code']} - {resp['msg']}"
                )
                device_list = []
                break
            device_resp_message = resp["msg"]
            device_list.extend(device_resp_message["items"])
            if len(device_list) == device_resp_message["total"]:
                conn.logger.info(
                    f"Total devices fetched from account: {len(device_list)}"
                )
                break
            offset += DEVICE_GET_LIMIT
        return device_list

    def get_device(
        self,
        conn,
        limit=DEVICE_GET_LIMIT,
        offset=0,
        filter=None,
        select=None,
        sort=None,
    ):
        """
        Get a list of devices managed in a GLP workspace from filter/select
        and sort inputs.
        Rate limits are enforced on this API. 160 requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param limit: specifies the number of results to be returned.
            The default value is 2000.
        :type limit: int
        :param offset: specifies the zero-based resource offset to start the
            response from. The default value is 0.
        :type offset: int
        :param filter: device filters joined by logical operators
        :type filter: str
        :param select: properties of devices to be displayed in response.
        :type select: list
        :param sort: sort string expressions
        :type sort: str

        :return: response as provided by 'command' function in
            class: `pycentral.NewCentralBase`
        :rtype: dict
        """

        conn.logger.info("Getting a device in GLP workspace")
        path = urls.GLP_DEVICES["DEFAULT"]

        params = {"limit": limit, "offset": offset}
        if filter:
            params["filter"] = filter
        if select:
            params["select"] = select
        if sort:
            params["sort"] = sort

        resp = conn.command("GET", path, "glp", api_params=params)
        if resp["code"] == 200:
            conn.logger.info("Get device successful!")
        else:
            conn.logger.error("Get device failed!")
        return resp

    def get_device_id(self, conn, serial):
        """
        Get device ID in a GLP workspace by serial.

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param serial: device serial
        :type serial: str

        :return: Tuple of two elements. First element of the tuple returns True
            if device id is found, else False. The second element is a GLP
            device ID if found. Else, an error message from the response.
        :rtype: (bool, str)
        """

        filter = f"serialNumber eq '{serial}'"
        resp = self.get_device(conn, filter=filter)
        if resp["code"] != 200:
            return (resp, (False, "Bad request for get_id"))
        elif resp["msg"]["count"] == 0:
            return (False, "Serial not found")
        else:
            return (True, resp["msg"]["items"][0]["id"])

    def get_status(self, conn, id):
        """
        Get status of an async GLP devices request.

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param id: transaction ID from async API request
        :type id: str

        :return: response as provided by 'command' function in
            class: `pycentral.NewCentralBase`
        :rtype: dict
        """

        path = urlJoin(urls.GLP_DEVICES["GET_ASYNC"], id)
        resp = conn.command("GET", path, "glp")
        return resp

    def add_devices(self, conn, network=[], compute=[], storage=[]):
        """
        Post devices to GLP workspace. Handles coordinating chaining requests
        if passed more than 5 devices(max per api call). Can use any
        combination of network, compute, and storage devices. Always return a
        202 response code if basic input validation is met. Currently does not
        support Async get status handling to confirm operation success.

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param network: network devices as dict objects
        :type network: list
        :param compute: compute devices as dict objects
        :type compute: list
        :param storage: storage devices as dict objects
        :type storage: list

        :return: list of resp objects as provided by 'command' function in
            class: `pycentral.NewCentralBase`
        :rtype: list
        """

        count = len(network) + len(compute) + len(storage)
        resp_list = []

        # Check for rate limit handler
        if count > INPUT_SIZE:
            conn.logger.info(
                "WARNING MORE THAN 5 DEVICES IS AN ALPHA FEATURE!"
            )
            resp_list.append(self.__add_dev("network", network))
            resp_list.append(self.__add_dev("compute", compute))
            resp_list.append(self.__add_dev("storage", storage))
            return resp_list
        else:
            path = urls.GLP_DEVICES["DEFAULT"]
            data = {"network": network, "compute": compute, "storage": storage}
            resp = conn.command("POST", path, "glp", api_data=data)
            resp_list.append(resp)
            if resp["code"] == 202:
                conn.logger.info("Add device request accepted...")
            else:
                conn.logger.error("Add device request failed!")
            return resp_list

    def __add_dev(self, conn, type, inputs):
        """
        Helper function for add_devices. Handles splitting inputs larger than
        input size and coordinates running the commands to not exceed rate
        limit.

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param type: one of network, compute, or storage
        :type param: str
        :param inputs: list of 'type' objects in dict format
        :type inputs: list

        :return: response object as provided by 'command' function in
            class: `pycentral.NewCentralBase`
        :rtype: list
        """

        path = urls.GLP_DEVICES["DEFAULT"]
        data = {"network": [], "compute": [], "storage": []}

        if len(inputs) > INPUT_SIZE:
            split_input, wait_time = rate_limit_check(
                inputs, INPUT_SIZE, POST_RPM
            )

            resp_list = []

            for devices in split_input:
                data["network"] = devices if type == "network" else []
                data["compute"] = devices if type == "compute" else []
                data["storage"] = devices if type == "storage" else []
                resp = conn.command("POST", path, "glp", api_data=data)
                if resp["code"] != 202:
                    conn.logger.error(
                        f"Add device request failed for {inputs}!"
                    )
                else:
                    conn.logger.info("Add device request accepted...")
                resp_list.append(resp)
                time.sleep(wait_time)
            return resp_list
        else:
            data["network"] = inputs if type == "network" else []
            data["compute"] = inputs if type == "compute" else []
            data["storage"] = inputs if type == "storage" else []

            resp = conn.command("POST", path, "glp", api_data=data)
            if resp["code"] != 202:
                conn.logger.error(f"Add device request failed for {inputs}!")
            else:
                conn.logger.info("Add device request accepted...")
            time.sleep(60 / POST_RPM)
            return resp

    def add_sub(self, conn, devices, sub, serial=False, key=False):
        """
        Add subscription to device(s). API endpoint supports five devices
        per request. Handles chaining multiple requests for greater than
        five devices supplied. An additional response dict object will be
        appended to the return list for each additional request required to
        handle the number of input devices passed to the function.

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param device: list of device id(s) or serial
        :type device: list
        :param sub: subscription id or key
        :type sub: str
        :param serial: flag to use device serial
        :type serial: bool
        :param key: flag to use subscription key
        :type key: bool

        :return: list of API response objects as provided by 'command' function
            in class: `pycentral.NewCentralBase`
        :rtype: list
        """

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        if key:
            s = Subscriptions()
            id = s.get_sub_id(conn, sub)
            if id[0]:
                sub = id[1]
            else:
                conn.logger.error("Get sub ID from key failed!")

        split_input, wait_time = None, None

        # Split devices list per input size.
        if len(devices) > INPUT_SIZE:
            split_input, wait_time = rate_limit_check(
                devices, INPUT_SIZE, PATCH_RPM
            )
            conn.logger.info("WARNING MORE THAN 5 DEVICES IS A BETA FEATURE!")

        # Setup variables for iterating commands.
        queue = [devices] if not split_input else split_input
        resp_list = []
        path = urls.GLP_DEVICES["DEFAULT"]
        body = {"subscription": [{"id": sub}]}

        for inputs in queue:
            params = {"id": inputs}

            resp = conn.command(
                "PATCH", path, "glp", api_params=params, api_data=body
            )
            if resp["code"] == 202:
                conn.logger.info("Add sub request accepted...")
                id = resp["msg"]["transactionId"]
                status = check_progress(conn, id, self, limit=PATCH_RPM)
                if status[0]:
                    conn.logger.info(
                        "Sucessfully added subscriptions to devices!"
                    )
                    resp_list.append(status[1])
                else:
                    conn.logger.error("Add subscription failed!")
                    resp_list.append(status[1])
            else:
                conn.logger.error("Bad request for add subscription!")
                resp_list.append(resp)

            if wait_time:
                time.sleep(wait_time)

        return resp_list

    def remove_sub(self, conn, devices, serial=False):
        """
        Remove a subscription from a device. API endpoint supports five devices
        per request. Handles chaining multiple requests for greater than
        five devices supplied. An additional response dict object will be
        appended to the return list for each additional request required to
        handle the number of input devices passed to the function.

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param devices: list of device(s) to remove sub
        :type devices: list
        :param serial: flag to use device serial
        :type serial: bool

        :return: list of API response objects as provided by 'command' function
            in class: `pycentral.NewCentralBase`
        :rtype: list
        """

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        split_input, wait_time = None, None

        # Split devices list per input size.
        if len(devices) > INPUT_SIZE:
            split_input, wait_time = rate_limit_check(
                devices, INPUT_SIZE, PATCH_RPM
            )
            conn.logger.info("WARNING MORE THAN 5 DEVICES IS A BETA FEATURE!")

        # Setup variables for iterating commands.
        queue = [devices] if not split_input else split_input
        resp_list = []
        path = urls.GLP_DEVICES["DEFAULT"]
        body = {"subscription": []}

        for inputs in queue:
            params = {"id": inputs}

            resp = conn.command(
                "PATCH", path, "glp", api_params=params, api_data=body
            )
            if resp["code"] == 202:
                conn.logger.info("Remove sub request accepted...")
                id = resp["msg"]["transactionId"]
                status = check_progress(conn, id, self, limit=PATCH_RPM)
                if status[0]:
                    conn.logger.info(
                        "Sucessfully Removed subscriptions from devices!"
                    )
                    resp_list.append(status[1])
                else:
                    conn.logger.error("Remove subscription failed!")
                    resp_list.append(status[1])
            else:
                conn.logger.error("Bad request for remove subscription!")
                resp_list.append(resp)

            if wait_time:
                time.sleep(wait_time)

        return resp_list

    def assign_devices(
        self, conn, devices=None, application=None, region=None, serial=False
    ):
        """
        Update devices by passing one or more device IDs. Currently supports assigning and un-assigning devices to and from an application or applying/removing subscriptions to/from devices.
        Rate limits are enforced on this API. Five requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

        :param devices: array of strings consisting of device serial numbers
        :type devices: array of strings
        :param application: application id
        :type application: string
        :param region: ahe region of the application the device is provisioned in.
        :type region: string
        :param serial: True or False value, deafult is set to True
        :type serial: boolean (Example: True)
        :return: API response
        :rtype: dict
        """
        conn.logger.info("Assigning device(s) to an application")
        path = urls.GLP_DEVICES["DEFAULT"]

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        if len(devices) > INPUT_SIZE:
            resp = []
            rate_check = rate_limit_check(devices, INPUT_SIZE, PATCH_RPM)
            queue, wait_time = rate_check

            for i in range(len(queue)):
                params = {"id": queue[i]}

                data = {"application": {"id": application}, "region": region}

                time.sleep(wait_time)

                resp.append(
                    conn.command(
                        api_method="PATCH",
                        api_path=path,
                        api_params=params,
                        api_data=data,
                        app_name="glp",
                    )
                )

        else:
            params = {"id": devices}

            data = {"application": {"id": application}, "region": region}

            resp = conn.command(
                api_method="PATCH",
                api_path=path,
                api_params=params,
                api_data=data,
                app_name="glp",
            )

        if resp["code"] == 202:
            conn.logger.info(
                "Assign device(s) to application request accepted..."
            )
            id = resp["msg"]["transactionId"]
            status = check_progress(conn, id, self, limit=PATCH_RPM)
            if status[0]:
                conn.logger.info(
                    "Sucessfully assigned device(s) to application!"
                )
                return status[1]
            else:
                conn.logger.error("Assign device(s) to application failed!")
                return status[1]
        conn.logger.error("Bad request for assign device(s) to application!")
        return resp

    def unassign_devices(self, conn, devices=None, serial=False):
        """
        Update devices by passing one or more device IDs. Currently supports assigning and un-assigning devices to and from an application or applying/removing subscriptions to/from devices.
        Rate limits are enforced on this API. Five requests per minute is supported per workspace. API will result in 429 if this threshold is breached.

        :param devices: array of strings consisting of device serial numbers
        :type devices: array of strings
        :param serial: True or False value, deafult is set to True
        :type serial: boolean (Example: True)
        :return: API response
        :rtype: dict
        """
        conn.logger.info("Unassigning device(s) from an application")
        path = urls.GLP_DEVICES["DEFAULT"]

        if serial:
            d_list = []
            for d in devices:
                id = self.get_device_id(conn, d)
                if id[0]:
                    d_list.append(id[1])
                else:
                    conn.logger.error("Get device ID from serial failed!")
            devices = d_list

        if len(devices) > INPUT_SIZE:
            resp = []
            rate_check = rate_limit_check(devices, INPUT_SIZE, PATCH_RPM)
            queue, wait_time = rate_check

            for i in range(len(queue)):
                params = {"id": queue[i]}

                data = {"application": {"id": None}, "region": None}

                time.sleep(wait_time)

                resp.append(
                    conn.command(
                        api_method="PATCH",
                        api_path=path,
                        api_params=params,
                        api_data=data,
                        app_name="glp",
                    )
                )

        else:
            params = {"id": devices}

            data = {"application": {"id": None}, "region": None}

            resp = conn.command(
                api_method="PATCH",
                api_path=path,
                api_params=params,
                api_data=data,
                app_name="glp",
            )

        if resp["code"] == 202:
            conn.logger.info("Unassign device(s) from application accepted...")
            id = resp["msg"]["transactionId"]
            status = check_progress(conn, id, self, limit=PATCH_RPM)
            if status[0]:
                conn.logger.info(
                    "Sucessfully unassigned device(s) from application!"
                )
                return status[1]
            else:
                conn.logger.error(
                    "Unassign device(s) from application failed!"
                )
                return status[1]
        conn.logger.error(
            "Bad request for unassign device(s) from application!"
        )
        return resp

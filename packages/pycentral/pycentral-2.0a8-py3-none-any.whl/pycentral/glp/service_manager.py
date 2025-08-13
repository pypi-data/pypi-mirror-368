# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.url_utils import NewCentralURLs

urls = NewCentralURLs()


class ServiceManager(object):
    def get_application_id_and_region(self, conn, application_name, region):
        """
        Retrieve the application ID and API region name for a specified application and region.
        This method performs the following steps:
        1. Validates that the `application_name` and `region` parameters are not empty.
        2. Fetches the list of service managers and their associated regions.
        3. Maps the provided region (UI name) to its corresponding API region name.
        4. Verifies if the specified application exists in the given region.
        5. Fetches the list of provisioned service managers and verifies if the application is installed in the specified region.
        :param region: The region (UI name) where the application is deployed.
        :returns: A dictionary containing the application ID and API region name if found, otherwise None.
        :rtype: dict or None
        """
        if not application_name or not region:
            conn.logger.error("Application name or region cannot be empty.")
            return None

        resp = self.get_service_manager_by_region(conn)
        if resp["code"] != 200:
            conn.logger.error(
                f"Error fetching list of service manager(applications) by region: {resp['code']} - {resp['msg']}"
            )
            return None

        region_service_manager_mapping = (
            self._generate_application_region_mapping(resp["msg"]["items"])
        )
        if region not in region_service_manager_mapping.keys():
            conn.logger.error(
                f"Unable to find region with name {region}. \nValid regions are {', '.join(region_service_manager_mapping.keys())}"
            )
            return None
        api_region_name = region_service_manager_mapping[region]["id"]

        region_service_managers = list(
            region_service_manager_mapping[region]["serviceManagers"].keys()
        )
        if application_name not in region_service_managers:
            conn.logger.error(
                f"Unable to find service manager with name {application_name}. \nValid service managers(applications) in region {region} are {', '.join(region_service_managers)}"
            )
            return None
        service_manager_id = region_service_manager_mapping[region][
            "serviceManagers"
        ][application_name]

        resp = self.get_service_manager_provisions(conn)
        if resp["code"] != 200:
            conn.logger.error(
                f"Error fetching list of service manager provisions (installed applications): {resp['code']} - {resp['msg']}"
            )
            return None
        for provisioned_service in resp["msg"]["items"]:
            if (
                service_manager_id
                == provisioned_service["serviceManager"]["id"]
                and provisioned_service["region"] == api_region_name
            ):
                conn.logger.info(
                    f"Successfully verified installation of service manager {application_name} in region {region}."
                )
                return {
                    "id": service_manager_id,
                    "region": api_region_name,
                }

        conn.logger.error(
            f"Unable to find service manager(application) with name {application_name} in region {region}."
        )
        return None

    def get_service_manager_provisions(self, conn, limit=2000, offset=0):
        """
        Retrieve all provisioned services in GLP workspace.

        :param conn: Connection object used to interact with the service.
        :type conn: object
        :param limit: Specify the maximum number of entries per page. NOTE: The maximum value accepted is 2000.
        :type limit: int
        :param offset: Specify pagination offset. An offset argument defines how many pages to skip before returning results.
        :type offset: int

        :returns: API response
        :rtype: dict
        """
        conn.logger.info("Getting provisioned services in GLP workspace")
        path = urls.GLP_SERVICES["SERVICE_MANAGER_PROVISIONS"]

        params = {
            "limit": limit,
            "offset": offset,
        }

        resp = conn.command(
            api_method="GET", api_path=path, api_params=params, app_name="glp"
        )
        return resp

    def get_service_manager_by_region(self, conn):
        """
        Get the region mapping for the service manager.

        :param conn: The connection object.
        :type conn: object

        :returns: API response
        :rtype: dict
        """
        conn.logger.info("Getting services managers by region in GLP")
        path = urls.GLP_SERVICES["SERVICE_MANAGER_BY_REGION"]

        resp = conn.command(api_method="GET", api_path=path, app_name="glp")
        return resp

    def _generate_application_region_mapping(self, service_manager_list):
        """
        Generates mappings for service managers and regions based on the provided service manager by region's API response.

        This method processes a list of regions, each containing service managers, to create two mappings:
        1. A mapping of service manager names to their corresponding IDs.
        2. A mapping of region names from UI to their corresponding API name.

        :param service_manager_list: A list of dictionaries, where each dictionary represents a region
            and contains its name, ID, and associated service managers.
        :type service_manager_list: list

        :returns: A dictionary mapping region names to their IDs.
        :rtype: dict
        """
        region_map = {}
        for region in service_manager_list:
            region_map[region["regionName"]] = {"id": region["id"]}
            region_map[region["regionName"]]["serviceManagers"] = {
                serviceManager["name"]: serviceManager["id"]
                for serviceManager in region["serviceManagers"]
            }

        return region_map

    def get_service_managers(self, conn, limit=2000, offset=0):
        """
        Retrieve all available service managers in GLP.

        :param conn: Connection object used to interact with the service.
        :type conn: object
        :param limit: Specify the maximum number of entries per page. NOTE: The maximum value accepted is 2000.
        :type limit: int
        :param offset: Specify pagination offset. An offset argument defines how many pages to skip before returning results.
        :type offset: int

        :returns: API response
        :rtype: dict
        """
        conn.logger.info("Getting service managers in GLP")
        path = urls.GLP_SERVICES["SERVICE_MANAGER"]

        params = {
            "limit": limit,
            "offset": offset,
        }

        resp = conn.command(
            api_method="GET", api_path=path, api_params=params, app_name="glp"
        )
        return resp

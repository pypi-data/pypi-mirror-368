# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils import NewCentralURLs

urls = NewCentralURLs()


class ScopeMaps:
    def __init__(self):
        pass

    # ? Should central_conn be stored in self
    def get(self, central_conn):
        """
        Perform a GET call to retrieve data for the Global Scope Map then sets
            attrs on ScopeMap Object based on data received

        :param central_conn: established Central connection object
        :type central_conn: NewCentralBase
        :return: Returns JSON Data of GET call if success, else None
        :rtype: dict
        """
        scope_maps_list = []
        api_method = "GET"
        api_path = urls.fetch_url("SCOPES", "SCOPE-MAPS")
        resp = central_conn.command(api_method=api_method, api_path=api_path)
        if resp["code"] == 200:
            for mapping in resp["msg"]["scope-map"]:
                mapping["scope-name"] = int(mapping["scope-name"])
            scope_maps_list = resp["msg"]["scope-map"]
        else:
            central_conn.logger.error(
                f"Unable to fetch scope maps data. Error code - {resp['code']}.\n Error Description - {resp['msg']}"
            )
        return scope_maps_list

    # ? should this return a value or set a value to self?
    def get_scope_assigned_profiles(self, central_conn, scope_id):
        """
        Performs a GET call to retrieve Global Scope Map then finds the
            matching scope based on the id provided

        :param central_conn: established Central connection object
        :type central_conn: NewCentralBase
        :param scope_id: id of the scope to be matched on
        :type scope_id: str
        """
        assigned_profiles = []
        mappings = self.get(central_conn=central_conn)
        if mappings:
            for mapping in mappings:
                if mapping["scope-name"] == scope_id:
                    assigned_profiles.append(mapping)
        for profile in assigned_profiles:
            profile.pop("scope-name")

    def associate_profile_to_scope(
        self, central_conn, scope_id, profile_name, persona
    ):
        """
        Performs a POST call to associate to a profile with the respective
            device persona to the provided scope.

        :param central_conn: established Central connection object
        :type central_conn: NewCentralBase
        :param scope_id: id of the scope to associate the profile
        :type scope_id: str
        :param profile_name: name of the profile to be assigned
        :type profile_name: str
        :param persona: device persona to be associated with the profile
        :type persona: str
        :return: Returns JSON Data of returned response from POST call
        :rtype: dict
        """
        api_method = "POST"
        api_path = urls.fetch_url("SCOPES", "SCOPE-MAPS")
        valid_personas = [
            "SERVICE_PERSONA",
            "HYBRID_NAC",
            "CORE_SWITCH",
            "BRIDGE",
            "CAMPUS_AP",
            "IOT",
            "MOBILITY_GW",
            "AGG_SWITCH",
            "BRANCH_GW",
            "VPNC",
            "ACCESS_SWITCH",
            "MICROBRANCH_AP",
        ]
        if isinstance(persona, list) or "ALL" in persona:
            if "ALL" in persona:
                persona = valid_personas
            for p in persona:
                if p not in valid_personas:
                    central_conn.logger.error(
                        f"{p} is not a valid device persona"
                        f"Unable to assign profile {profile_name} to "
                        f"{scope_id}"
                    )
                api_data = {
                    "scope-map": [
                        {
                            "scope-name": str(scope_id),
                            "persona": p,
                            "resource": profile_name,
                        }
                    ]
                }
                resp = central_conn.command(
                    api_method=api_method, api_path=api_path, api_data=api_data
                )
                if resp["code"] == 200:
                    central_conn.logger.info(
                        f"Successfully assigned profile {profile_name} to"
                        f" {scope_id} with {p} device persona"
                    )
        else:
            api_data = {
                "scope-map": [
                    {
                        "scope-name": str(scope_id),
                        "persona": persona,
                        "resource": profile_name,
                    }
                ]
            }

            resp = central_conn.command(
                api_method=api_method, api_path=api_path, api_data=api_data
            )

            if resp["code"] == 200:
                central_conn.logger.info(
                    f"Successfully assigned profile {profile_name} to "
                    f"{scope_id} with {persona} device persona"
                )
        return resp

    def unassociate_profile_from_scope(
        self, central_conn, scope_id, profile_name, persona
    ):
        """
        Performs a DELETE call to unassign a profile with the respective
            device persona from the provided scope.

        :param central_conn: established Central connection object
        :type central_conn: NewCentralBase
        :param scope_id: id of the scope to associate the profile
        :type scope_id: str
        :param profile_name: name of the profile to be assigned
        :type profile_name: str
        :param persona: device persona to be associated with the profile
        :type persona: str
        :return: Returns JSON Data of returned response from DELETE call
        :rtype: dict
        """
        api_method = "DELETE"
        api_path = urls.fetch_url("SCOPES", "SCOPE-MAPS")
        valid_personas = [
            "SERVICE_PERSONA",
            "HYBRID_NAC",
            "CORE_SWITCH",
            "BRIDGE",
            "CAMPUS_AP",
            "IOT",
            "MOBILITY_GW",
            "AGG_SWITCH",
            "BRANCH_GW",
            "VPNC",
            "ACCESS_SWITCH",
            "MICROBRANCH_AP",
        ]
        if isinstance(persona, list) or "ALL" in persona:
            if "ALL" in persona:
                persona = valid_personas
            for p in persona:
                if p not in valid_personas:
                    central_conn.logger.error(
                        f"{p} is not a valid device persona"
                        f"Unable to unassign profile {profile_name} from"
                        f" {scope_id}"
                    )
                api_data = {
                    "scope-map": [
                        {
                            "scope-name": str(scope_id),
                            "persona": p,
                            "resource": profile_name,
                        }
                    ]
                }
                resp = central_conn.command(
                    api_method=api_method, api_path=api_path, api_data=api_data
                )

                if resp["code"] == 200:
                    central_conn.logger.info(
                        f"Successfully unassigned profile {profile_name} from"
                        f" {scope_id} with {p} device persona"
                    )
        else:
            api_data = {
                "scope-map": [
                    {
                        "scope-name": str(scope_id),
                        "persona": persona,
                        "resource": profile_name,
                    }
                ]
            }

            resp = central_conn.command(
                api_method=api_method, api_path=api_path, api_data=api_data
            )

            if resp["code"] == 200:
                central_conn.logger.info(
                    f"Successfully unassigned profile {profile_name} from"
                    f" {scope_id} with {persona} device persona"
                )
        return resp

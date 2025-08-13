# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .url_utils import NETWORKING_PREFIX


class ProfilesUtils:
    PROFILES = {
        "SYSTEM_INFO": {"resource": "system-info", "bulk_key": None},
        "VLAN": {"resource": "layer2-vlan", "bulk_key": "l2-vlan"},
        "WLAN": {"resource": "wlan-ssids", "bulk_key": "wlan-ssid"},
        "ROLE": {"resource": "roles", "bulk_key": "role"},
        "NTP": {"resource": "ntp", "bulk_key": "profile"},
        "POLICY": {"resource": "policies", "bulk_key": "policy"},
    }

    def get_resource(self, api_category):
        if api_category in self.PROFILES:
            return self.PROFILES[api_category]["resource"]
        else:
            raise ValueError(f"Invalid API category: {api_category}")

    def get_bulk_key(self, api_category):
        if api_category in self.PROFILES:
            return self.PROFILES[api_category]["bulk_key"]
        else:
            raise ValueError(f"Invalid API category: {api_category}")

    def fetch_profile_url(self, api_name, resource_name=None):
        api_url = NETWORKING_PREFIX
        if api_name in self.PROFILES:
            api_url += self.PROFILES[api_name]["resource"]
            if resource_name:
                api_url += "/" + resource_name

        return api_url


def validate_local(local):
    local_attributes = dict()
    required_local_keys = ["scope_id", "persona"]
    if local is not None and all(key in local for key in required_local_keys):
        local_attributes = {"object_type": "LOCAL"}
        local_attributes.update(local)

    return local_attributes

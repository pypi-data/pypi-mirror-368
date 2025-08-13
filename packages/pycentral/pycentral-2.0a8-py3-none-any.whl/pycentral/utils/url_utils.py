# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

NETWORKING_PREFIX = "network-config/v1alpha1/"

category_mapping = {
    "monitoring": "network-monitoring/v1alpha1/",
    "configuration": "network-config/v1alpha1/",
    "troubleshooting": "network-troubleshooting/v1alpha1/",
}


def urlJoin(*args):
    trailing_slash = "/" if args[-1].endswith("/") else ""
    return (
        "/" + "/".join(map(lambda x: str(x).strip("/"), args)) + trailing_slash
    )


class NewCentralURLs:
    Authentication = {
        "OAUTH": "https://sso.common.cloud.hpe.com/as/token.oauth2"
    }

    GLP = {"BaseURL": "https://global.api.greenlake.hpe.com"}

    GLP_DEVICES = {
        "DEFAULT": "/devices/v1/devices",
        # full url requires {id} to be passed as param: /devices/v1/async-operations/{id}
        "GET_ASYNC": "/devices/v1/async-operations/",
    }

    GLP_SUBSCRIPTION = {
        "DEFAULT": "/subscriptions/v1/subscriptions",
        # full url requires {id} to be passed as param: /devices/v1/async-operations/{id}
        "GET_ASYNC": "/subscriptions/v1/async-operations/",
    }

    GLP_USER_MANAGEMENT = {
        "GET": "/identity/v1/users",
        # full url requires {id} to be passed as param: /identity/v1/users/{id}
        "GET_USER": "/identity/v1/users/",
        "POST": "/identity/v1/users",
        # full url requires {id} to be passed as param: /identity/v1/users/{id}
        "PUT": "/identity/v1/users/",
        # full url requires {id} to be passed as param: /identity/v1/users/{id}
        "DELETE": "/identity/v1/users/",
    }

    GLP_SERVICES = {
        "SERVICE_MANAGER": "/service-catalog/v1/service-managers",
        "SERVICE_MANAGER_PROVISIONS": "/service-catalog/v1/service-manager-provisions",
        "SERVICE_MANAGER_BY_REGION": "/service-catalog/v1/per-region-service-managers",
    }
    SCOPES = {
        "SITE": "sites",
        "SITE_COLLECTION": "site-collections",
        "DEVICE": "devices",
        "DEVICE_GROUP": "device-collections",
        "ADD_SITE_TO_COLLECTION": "site-collection-add-sites",
        "REMOVE_SITE_FROM_COLLECTION": "site-collection-remove-sites",
        "HIERARCHY": "hierarchy",
        "SCOPE-MAPS": "scope-maps",
    }

    def fetch_url(self, api_category, api_name):
        api_url = NETWORKING_PREFIX
        if hasattr(self, api_category):
            api_category = getattr(self, api_category)
            if api_name in api_category:
                api_url += api_category[api_name]

        return api_url

    @staticmethod
    def generate_url(api_endpoint):
        if api_endpoint is not None and not isinstance(api_endpoint, str):
            print("API endpoint should be a string")
            exit()
        api_url = NETWORKING_PREFIX + api_endpoint
        return api_url


@staticmethod
def generate_url_with_params(category, api_endpoint):
    if category not in category_mapping:
        raise ValueError(
            f"Invalid category: {category}, Supported categories: {list(category_mapping.keys())}  "
        )
    return category_mapping[category] + api_endpoint

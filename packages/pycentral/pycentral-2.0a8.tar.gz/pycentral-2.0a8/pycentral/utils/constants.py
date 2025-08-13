# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

# Dictionary of Public HPE Aruba Networking cluster naames with their corresponding API Base
# URLs. You can update this dictionary, if you want to add your own private
# cluster details. You can learn more about Base URLs here - https://developer.arubanetworks.com/new-hpe-anw-central/docs/getting-started-with-rest-apis#api-gateway-base-urls
CLUSTER_BASE_URLS = {
    "EU-1": "https://ge1.api.central.arubanetworks.com",
    "EU-Central2": "https://ge2.api.central.arubanetworks.com",
    "EU-Central3": "https://ge3.api.central.arubanetworks.com",
    "US-1": "https://us1.api.central.arubanetworks.com",
    "US-2": "https://us2.api.central.arubanetworks.com",
    "US-WEST-4": "https://us4.api.central.arubanetworks.com",
    "US-WEST-5": "https://us5.api.central.arubanetworks.com",
    "US-East1": "https://us6.api.central.arubanetworks.com",
    "Canada-1": "https://cn1.api.central.arubanetworks.com",
    "APAC-1": "https://in.api.central.arubanetworks.com",
    "APAC-EAST1": "https://jp1.api.central.arubanetworks.com",
    "APAC-SOUTH1": "https://au1.api.central.arubanetworks.com",
    "Internal": "https://internal.api.central.arubanetworks.com",
}

# Dictionary of supported device personas and their corresponding API values.
SUPPORTED_CONFIG_PERSONAS = {
    "Campus AP": "CAMPUS_AP",
    "Micro Branch AP": "MICROBRANCH_AP",
    "Access Switch": "ACCESS_SWITCH",
    "Core Switch": "CORE_SWITCH",
    "Aggregation Switch": "AGG_SWITCH",
    "Mobility GW": "MOBILITY_GW",
    "Branch GW": "BRANCH_GW",
    "Bridge": "BRIDGE",
    "Hybrid NAC": "HYBRID_NAC",
}

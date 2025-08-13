# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

SUPPORTED_DEVICE_TYPES = ["aos-s", "cx", "aps", "gateways"]

TROUBLESHOOTING_METHOD_DEVICE_MAPPING = {
    "initiate_retrieve_arp_table_test": ["aos-s", "aps", "gateways"],
    "locate_test": ["cx", "aps", "gateways"],
    "http_test": ["cx", "aps", "gateways"],
    "poe_bounce_test": ["cx", "aos-s", "gateways"],
    "port_bounce_test": ["cx", "aos-s", "gateways"],
    "speedtest_test": ["aps"],
    "aaa_test": ["cx"],
    "tcp_test": ["aps"],
    "iperf_test": ["gateways"],
    "cable_test": ["cx", "aos-s"],
}

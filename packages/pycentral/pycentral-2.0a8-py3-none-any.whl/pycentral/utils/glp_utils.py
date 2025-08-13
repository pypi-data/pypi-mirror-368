# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .base_utils import console_logger

import time

DEVICE_LIMIT = 20
SUB_LIMIT = 5

logger = console_logger("RATE LIMIT CHECK")


def rate_limit_check(input_array, input_size_limit, rate_per_minute):
    print("Attempting to bypass rate limit")
    queue = []
    wait_time = []

    for i in range(0, len(input_array), input_size_limit):
        sub_array = input_array[i : i + input_size_limit]
        queue.append(sub_array)

    if len(queue) > rate_per_minute:
        wait_time = 60 / rate_per_minute
        print(
            "Array size exceeded,",
            wait_time,
            "second wait timer implemented per request to prevent errors",
        )
        print("Loading ...")
    else:
        wait_time = 0

    return queue, wait_time


def check_progress(conn, id, module_instance, limit=None):
    """
    check progress of async glp api.

    :param conn: new pycentral base object
    :param id: async transaction id
    :param module_instance: instance of the module class (Devices or Subscriptions)
    :param limit: rate limit for the module

    :return: tuple, (True or False for operation result, api response)
    """

    if limit is None:
        if module_instance.__class__.__name__ == "Devices":
            limit = DEVICE_LIMIT
        elif module_instance.__class__.__name__ == "Subscriptions":
            limit = SUB_LIMIT
        else:
            raise ValueError(
                "module_instance must be an instance of Devices or Subscription"
            )

    updated = False
    while not updated:
        status = module_instance.get_status(conn, id)
        if status["code"] != 200:
            conn.logger.error(
                f"Bad request for get async status with transaction {id}!"
            )
            return (False, status)
        elif status["msg"]["status"] == "SUCCEEDED":
            updated = True
            return (True, status)
        elif status["msg"]["status"] == "TIMEOUT":
            updated = True
            conn.logger.error(
                f"Async operation timed out for transaction {id}!"
            )
            return (False, status)
        elif status["msg"]["status"] == "FAILED":
            updated = True
            conn.logger.error(f"Async operation failed for transaction {id}!")
            return (False, status)
        else:
            # Sleep time calculated by async rate limit.
            sleep_time = 60 / limit
            time.sleep(sleep_time)

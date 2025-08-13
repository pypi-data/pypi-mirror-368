# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from typing import Any


class PycentralError(Exception):
    """
    Base class for other PYCENTRAL exceptions.
    """

    base_msg = "PYCENTRAL ERROR"

    def __init__(self, *args):
        self.message = ", ".join(
            (
                self.base_msg,
                *(str(a) for a in args),
            )
        )
        self.response = None

    def __setattr__(self, name: str, value: Any) -> None:
        return super().__setattr__(name, value)

    def __str__(self):
        return repr(self.message)

    def set_response(self, response):
        self.response = response

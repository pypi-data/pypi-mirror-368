# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from pycentral.exceptions.verification_error import VerificationError


class ParameterError(VerificationError):
    """
    Exception raised when wrong parameters are passed to functions.
    """

    base_msg = "PARAMETER ERROR"

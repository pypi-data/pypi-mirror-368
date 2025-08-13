# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

import oauthlib
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
import json
import requests
from .utils.base_utils import (
    build_url,
    new_parse_input_args,
    console_logger,
    save_access_token,
)
from .scopes import Scopes
from .utils.url_utils import NewCentralURLs
from .exceptions import LoginError, ResponseError

urls = NewCentralURLs()
SUPPORTED_API_METHODS = ("POST", "PATCH", "DELETE", "GET", "PUT")


class NewCentralBase:
    def __init__(
        self, token_info, logger=None, log_level="DEBUG", enable_scope=False
    ):
        """
        This constructor initializes the NewCentralBase class with token information, logging configuration,
        and optional scope management. It validates and processes the provided token information, sets up
        logging, and optionally initializes scope-related functionality.

        :param token_info: Dictionary containing token information for supported applications - new_central, glp.
                  Can also be a string path to a YAML or JSON file with token information.
        :type token_info: dict or str
        :param logger: Logger instance, defaults to None.
        :type logger: logging.Logger, optional
        :param log_level: Logging level, defaults to "DEBUG".
        :type log_level: str, optional
        :param enable_scope: Flag to enable scope management. If True, the SDK will automatically fetch data
                             about existing scopes and associated profiles, simplifying scope and configuration
                             management. If False, scope-related API calls are disabled, resulting in faster
                             initialization. Defaults to False.
        :type enable_scope: bool, optional
        """
        self.token_info = new_parse_input_args(token_info)
        self.token_file_path = None
        if isinstance(token_info, str):
            self.token_file_path = token_info
        self.logger = self.set_logger(log_level, logger)
        self.scopes = None
        for app in self.token_info:
            app_token_info = self.token_info[app]
            if (
                "access_token" not in app_token_info
                or app_token_info["access_token"] is None
            ):
                self.create_token(app)
        if enable_scope:
            self.scopes = Scopes(central_conn=self)

    def set_logger(self, log_level, logger=None):
        """
        Set up the logger.

        :param log_level: Logging level.
        :type log_level: str
        :param logger: Logger instance, defaults to None.
        :type logger: logging.Logger, optional
        :return: Logger instance.
        :rtype: logging.Logger
        """
        if logger:
            return logger
        else:
            return console_logger("NEW CENTRAL BASE", log_level)

    def create_token(self, app_name):
        """
        Create a new access token for the specified application.

        This function generates a new access token using the client credentials
        for the specified application, updates the `self.token_info` dictionary
        with the new token, and optionally saves it to a file. The token is also
        returned.

        :param app_name: Name of the application. Supported applications: "new_central", "glp".
        :type app_name: str
        :return: Access token.
        :rtype: str
        :raises LoginError: If there is an error during token creation.
        :raises SystemExit: If invalid client credentials are provided.
        """
        client_id, client_secret = self._return_client_credentials(app_name)
        client = BackendApplicationClient(client_id)

        oauth = OAuth2Session(client=client)
        auth = HTTPBasicAuth(client_id, client_secret)

        try:
            self.logger.info(f"Attempting to create new token from {app_name}")
            token = oauth.fetch_token(
                token_url=urls.Authentication["OAUTH"], auth=auth
            )

            if "access_token" in token:
                self.logger.info(
                    f"{app_name} Login Successful.. Obtained Access Token!"
                )
                self.token_info[app_name]["access_token"] = token[
                    "access_token"
                ]
                if self.token_file_path:
                    save_access_token(
                        app_name,
                        token["access_token"],
                        self.token_file_path,
                        self.logger,
                    )
                return token["access_token"]
        except oauthlib.oauth2.rfc6749.errors.InvalidClientError:
            exitString = (
                "Invalid client_id or client_secret provided for "
                + app_name
                + ". Please provide valid credentials to create an access token."
            )
            exit(exitString)
        except Exception as e:
            raise LoginError(e)

    def handle_expired_token(self, app_name):
        """
        Handle expired access token by creating a new one.

        :param app_name: Name of the application.
        :type app_name: str
        """
        self.logger.info(
            f"{app_name} access Token has expired. Handling Token Expiry..."
        )
        client_id, client_secret = self._return_client_credentials(app_name)
        if any(
            credential is None for credential in [client_id, client_secret]
        ):
            exit(
                f"Please provide client_id and client_secret in {app_name} required to generate an access token"
            )
        else:
            self.create_token(app_name)

    def command(
        self,
        api_method,
        api_path,
        app_name="new_central",
        api_data={},
        api_params={},
        headers={},
        files={},
    ):
        """
        Execute an API command.

        :param api_method: HTTP method for the API call.
        :type api_method: str
        :param api_path: API endpoint path.
        :type api_path: str
        :param app_name: Name of the application, defaults to "new_central". If you need to make API call to GLP, set this attribute to glp
        :type app_name: str, optional
        :param api_data: Data to be sent in the API request, defaults to {}.
        :type api_data: dict, optional
        :param api_params: URL parameters for the API request, defaults to {}.
        :type api_params: dict, optional
        :param headers: HTTP headers for the API request, defaults to {}.
        :type headers: dict, optional
        :param files: Files to be sent in the API request, defaults to {}.
        :type files: dict, optional
        :return: Result of the API call.
        :rtype: dict
        :raises ResponseError: If there is an error during the API call.
        """
        self._validate_request(app_name, api_method)

        retry = 0
        result = ""

        limit_reached = False
        try:
            while not limit_reached:
                url = build_url(
                    self.token_info[app_name]["base_url"], api_path
                )

                if not headers and not files:
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                if api_data and headers["Content-Type"] == "application/json":
                    api_data = json.dumps(api_data)

                resp = self.request_url(
                    url=url,
                    data=api_data,
                    method=api_method,
                    headers=headers,
                    params=api_params,
                    files=files,
                    access_token=self.token_info[app_name]["access_token"],
                )
                if resp.status_code == 401:
                    self.logger.error(
                        "Received error 401 on requesting url "
                        "%s with resp %s" % (str(url), str(resp.text))
                    )
                    if retry >= 1:
                        limit_reached = True
                        break
                    self.handle_expired_token(app_name)
                    retry += 1
                else:
                    break

            result = {
                "code": resp.status_code,
                "msg": resp.text,
                "headers": dict(resp.headers),
            }

            try:
                result["msg"] = json.loads(result["msg"])
            except BaseException:
                result["msg"] = str(resp.text)

            return result

        except Exception as err:
            err_str = f"{api_method} FAILURE "
            self.logger.error(err)
            raise ResponseError(err_str, err)

    def request_url(
        self,
        url,
        access_token,
        data={},
        method="GET",
        headers={},
        params={},
        files={},
    ):
        """
        Make an API call to application(New Central or GLP) via the requests library.

        :param url: HTTP Request URL string.
        :type url: str
        :param access_token: Access token for authentication.
        :type access_token: str
        :param data: HTTP Request payload, defaults to {}.
        :type data: dict, optional
        :param method: HTTP Request Method supported by GLP/New Central, defaults to "GET".
        :type method: str, optional
        :param headers: HTTP Request headers, defaults to {}.
        :type headers: dict, optional
        :param params: HTTP URL query parameters, defaults to {}.
        :type params: dict, optional
        :param files: Files dictionary with file pointer depending on API endpoint as accepted by GLP/New Central, defaults to {}.
        :type files: dict, optional
        :return: HTTP response of API call using requests library.
        :rtype: requests.models.Response
        :raises ResponseError: If there is an error during the API call.
        """
        resp = None

        auth = BearerAuth(access_token)
        s = requests.Session()
        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            auth=auth,
            params=params,
            data=data,
        )
        prepped = s.prepare_request(req)
        settings = s.merge_environment_settings(
            prepped.url, {}, None, True, None
        )
        try:
            resp = s.send(prepped, **settings)
            return resp
        except Exception as err:
            str1 = "Failed making request to URL %s " % url
            str2 = "with error %s" % str(err)
            err_str = f"{str1} {str2}"
            self.logger.error(str1 + str2)
            raise ResponseError(err_str, err)

    def _validate_request(self, app_name, method):
        """
        Validate that provided app has access_token and a valid HTTP method.

        :param app_name: Name of the application.
        :type app_name: str
        :param method: HTTP method to be validated.
        :type method: str
        :raises ValueError: If app_name is not in token_info or access_token is missing for provided app_name.
        :raises ValueError: If the method is not supported.
        """
        if app_name not in self.token_info:
            error_string = (
                f"Missing access_token for {app_name}. Please provide access token "
                f"or client credentials to generate an access token for app - {app_name}"
            )
            self.logger.error(error_string)
            raise ValueError(error_string)

        if method not in SUPPORTED_API_METHODS:
            error_string = (
                f"HTTP method '{method}' not supported. Please provide an API with one of the "
                f"supported methods - {', '.join(SUPPORTED_API_METHODS)}"
            )
            self.logger.error(error_string)
            raise ValueError(error_string)

    def _return_client_credentials(self, app_name):
        """
        Return client credentials for the specified application.

        :param app_name: Name of the application.
        :type app_name: str
        :return: Client ID and client secret.
        :rtype: tuple
        """
        app_token_info = self.token_info[app_name]
        if all(
            client_key in app_token_info
            for client_key in ("client_id", "client_secret")
        ):
            client_id = app_token_info["client_id"]
            client_secret = app_token_info["client_secret"]
            return client_id, client_secret

    def get_scopes(self):
        """
        Sets up the scopes for the current instance by creating a Scopes object.

        This method initializes the `scopes` attribute using the `Scopes` class,
        passing the current instance (`self`) as the `central_conn` parameter.
        If the `scopes` attribute is already initialized, it simply returns the existing object.

        Returns:
            Scopes: The initialized or existing Scopes object.
        """
        if self.scopes is None:
            self.scopes = Scopes(central_conn=self)
        return self.scopes


class BearerAuth(requests.auth.AuthBase):
    """This class uses Bearer Auth method to generate the authorization header
    from New Central or GLP Access Token.

    :param token: New Central or GLP Access Token
    :type token: str
    """

    def __init__(self, token):
        """
        Constructor Method.

        :param token: New Central or GLP Access Token
        :type token: str
        """
        self.token = token

    def __call__(self, r):
        """
        Internal method returning auth.

        :param r: Request object.
        :type r: requests.models.PreparedRequest
        :return: Modified request object with authorization header.
        :rtype: requests.models.PreparedRequest
        """
        r.headers["authorization"] = "Bearer " + self.token
        return r

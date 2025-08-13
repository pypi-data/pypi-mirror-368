# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from ..utils.url_utils import NewCentralURLs, urlJoin

urls = NewCentralURLs()


class UserMgmt(object):
    def get_users(self, conn, filter=None, limit=300, offset=0):
        conn.logger.info("Getting users in GLP workspace")
        """
        Retrieve users that match given filters. All users are returned when no filters are provided.

        :param filter: Filter data using a subset of OData 4.0 and return only the subset of resources that match the filter. The Get users API can be filtered by: id, username, userStatus, createdAt, updatedAt, lastLogin
        :type filter: string (Example: 
            Filter with id
            Returns the user with a specific ID.
            filter=id eq '7600415a-8876-5722-9f3c-b0fd11112283'
            Filter with username
            Returns the user with a specific username.
            filter=username eq 'user@example.com'
            Filter with userStatus
            Returns users that are not unverified.
            filter=userStatus neq 'UNVERIFIED'
            Filter with createdAt
            Returns users created after 2020-09-21T14:19:09.769747
            filter=createdAt gt '2020-09-21T14:19:09.769747'
            Filter with updatedAt
            Returns users updated after 2020-09-21T14:19:09.769747
            filter=updatedAt gt '2020-09-21T14:19:09.769747'
            Filter with lastLogin
            Returns users that logged in before 2020-09-21T14:19:09.769747
            filter=lastLogin lt '2020-09-21T14:19:09.769747')
        :param limit: Specify the maximum number of entries per page. NOTE: The maximum value accepted is 300.
        :type limit: integer (Pagination limit) [ 1 .. 300 ]
        :param offset: Specify pagination offset. An offset argument defines how many pages to skip before returning results.
        :type offset: integer (Pagination offset) >= 0
        :return: API response
        :rtype: dict
        """
        path = urls.GLP_USER_MANAGEMENT["GET"]

        params = {
            "limit": limit,
            "offset": offset,
        }
        if filter:
            params["filter"] = filter

        resp = conn.command(
            api_method="GET", api_path=path, api_params=params, app_name="glp"
        )
        return resp

    def get_user(self, conn, email=None, id=None):
        conn.logger.info("Getting a user in GLP workspace")
        """
        Get a user from a workspace.

        :param email: account username (email address)
        :type email: string
        :param id: target user id
        :type id: string
        :return: response object as provided by 'command' function in
            class: `pycentral.NewCentralBase`
        :rtype: dict
        """
        if email:
            id = self.get_user_id(conn, email)[1]

        path = urlJoin(urls.GLP_USER_MANAGEMENT["GET_USER"], id)

        resp = conn.command("GET", path, "glp")
        if resp["code"] == 200:
            conn.logger.info("Get user successful!")
        else:
            conn.logger.error("Get user failed!")
        return resp

    def get_user_id(self, conn, email):
        """
        Get user ID in a GLP workspace by email

        :param conn: new pycentral base object
        :type conn: class: `pycentral.NewCentralBase`
        :param email: account username (email address)
        :type email: string
        :return: Tuple of two elements. First element of the tuple returns True
            if user id is found, else False. The second element is a GLP
            user ID if found. Else, an error message from the response.
        :rtype: (bool, str)
        """

        filter = f"username eq '{email}'"
        resp = self.get_users(conn, filter=filter)
        if resp["code"] != 200:
            return (resp, (False, "Bad request for get_id"))
        elif resp["msg"]["count"] == 0:
            return (False, "Email not found")
        else:
            return (True, resp["msg"]["items"][0]["id"])

    def delete_user(self, conn, email=None, user_id=None):
        conn.logger.info("Deleting a user in GLP workspace")
        """
        Delete a user from a workspace.

        :param email: account username (email address)
        :type email: string
        :param id: target user id
        :type id: string
        :return: API response
        :rtype: dict
        """
        if email:
            user_id = self.get_user_id(conn, email)[1]

        path = urlJoin(urls.GLP_USER_MANAGEMENT["DELETE"], user_id)
        resp = conn.command(api_method="DELETE", api_path=path, app_name="glp")
        return resp

    def inv_user(self, conn, email, send_link):
        conn.logger.info("Inviting a user to GLP workspace")
        """
        Invite a user to a GLP workspace.

        :param email: email address
        :type email: string
        :param send_link: set to send welcome email 
        :type send_link: boolean (Example: true)
        :return: response as provided by 'command' function in
            class: `pycentral.NewCentralBase`
        :rtype: dict
        """

        path = urls.GLP_USER_MANAGEMENT["POST"]
        body = {"email": email, "sendWelcomeEmail": send_link}

        resp = conn.command("POST", path, "glp", api_data=body)
        if resp["code"] == 200:
            conn.logger.info("Invite user successful!")
        else:
            conn.logger.error("Invite user failed!")
        return resp

# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class InternalController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(InternalController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def create_refresh_bulletin_board(self):
        """Does a POST request to /refresh-bulletin-board.

        Refresh bulletin board from Helios.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_refresh_bulletin_board called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_refresh_bulletin_board.')
            _url_path = '/refresh-bulletin-board'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for create_refresh_bulletin_board.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_refresh_bulletin_board.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_refresh_bulletin_board')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_refresh_bulletin_board.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
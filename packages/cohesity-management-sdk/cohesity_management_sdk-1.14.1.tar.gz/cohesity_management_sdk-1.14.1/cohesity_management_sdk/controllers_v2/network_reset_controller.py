# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.node_reset_state import NodeResetState
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class NetworkResetController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(NetworkResetController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def create_reset_nodes_network(self,
                                   body):
        """Does a POST request to /networkReset.

        This is destructive operation. Reset nodes' networking in cluster to
        factory state or cancel the reset operation.

        Args:
            body (ResetOrRestoreNetworking): Request to reset or restore
                cluster networking.

        Returns:
            void: Response from the API. Request Accepted

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_reset_nodes_network called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_reset_nodes_network.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_reset_nodes_network.')
            _url_path = '/networkReset'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_reset_nodes_network.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_reset_nodes_network.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_reset_nodes_network')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_reset_nodes_network.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_network_reset_states(self):
        """Does a GET request to /networkReset/status.

        Get networking reset state status.

        Returns:
            list of NodeResetState: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_network_reset_states called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_network_reset_states.')
            _url_path = '/networkReset/status'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_network_reset_states.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_network_reset_states.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_network_reset_states')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_network_reset_states.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NodeResetState.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

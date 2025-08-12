# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.update_fleet_env_info_request import UpdateFleetEnvInfoRequest
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class FleetInstanceController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(FleetInstanceController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def update_fleet_env_info(self,
                              body):
        """Does a POST request to /fleet-env-info.

        Add fleet environment info to cluster.

        Args:
            body (UpdateFleetEnvInfoRequest): Specifies the parameters to add
                fleet env info.

        Returns:
            UpdateFleetEnvInfoRequest: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_fleet_env_info called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_fleet_env_info.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_fleet_env_info.')
            _url_path = '/fleet-env-info'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_fleet_env_info.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_fleet_env_info.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_fleet_env_info')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_fleet_env_info.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, UpdateFleetEnvInfoRequest.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

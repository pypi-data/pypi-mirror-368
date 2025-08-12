# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.swift_params import SwiftParams
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class TenantsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(TenantsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_tenant_swift(self,
                         tenant_id=None):
        """Does a GET request to /tenants/swift.

        Get a Swift configuration.

        Args:
            tenant_id (string, optional): Specifies the tenant Id.

        Returns:
            SwiftParams: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tenant_swift called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tenant_swift.')
            _url_path = '/tenants/swift'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'tenantId': tenant_id
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tenant_swift.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tenant_swift.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tenant_swift')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tenant_swift.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SwiftParams.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_tenant_swift(self,
                            body):
        """Does a PUT request to /tenants/swift.

        Update a Swift configuration.

        Args:
            body (SwiftParams): Specifies the parameters to update a Swift
                configuration.

        Returns:
            SwiftParams: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_tenant_swift called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_tenant_swift.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_tenant_swift.')
            _url_path = '/tenants/swift'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_tenant_swift.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_tenant_swift.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_tenant_swift')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_tenant_swift.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SwiftParams.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

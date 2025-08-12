# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.keystones import Keystones
from cohesity_management_sdk.models_v2.keystone import Keystone
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class KeystoneController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(KeystoneController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_keystones(self,
                      names=None,
                      tenant_ids=None,
                      include_tenants=None):
        """Does a GET request to /keystones.

        Get Keystones.

        Args:
            names (list of string, optional): Specifies a list of Keystone
                names.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Keystones which were created by all tenants which the
                current user has permission to see. If false, then only
                Keystones created by the current user will be returned.

        Returns:
            Keystones: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_keystones called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_keystones.')
            _url_path = '/keystones'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'names': names,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_keystones.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_keystones.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_keystones')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_keystones.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Keystones.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_keystone(self,
                        body):
        """Does a POST request to /keystones.

        Create a Keystone configuration.

        Args:
            body (Keystone): Specifies the paremters to create a Keystone
                configuration.

        Returns:
            Keystone: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_keystone called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_keystone.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_keystone.')
            _url_path = '/keystones'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_keystone.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_keystone.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_keystone')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_keystone.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Keystone.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_keystones_by_id(self,
                            id):
        """Does a GET request to /keystones/{id}.

        Get a Keystone by its id.

        Args:
            id (long|int): Specifies the Keystone id.

        Returns:
            Keystone: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_keystones_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_keystones_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_keystones_by_id.')
            _url_path = '/keystones/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_keystones_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_keystones_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_keystones_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_keystones_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Keystone.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_keystone(self,
                        id,
                        body):
        """Does a PUT request to /keystones/{id}.

        Update a Keystone configuration.

        Args:
            id (long|int): Specifies the Keystone id.
            body (Keystone): Specifies the paremters to update a Keystone
                configuration.

        Returns:
            Keystone: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_keystone called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_keystone.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_keystone.')
            _url_path = '/keystones/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_keystone.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_keystone.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_keystone')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_keystone.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Keystone.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_keystone(self,
                        id,
                        admin_password):
        """Does a DELETE request to /keystones/{id}.

        Delete a Keystone configuration.

        Args:
            id (long|int): Specifies the Keystone id.
            admin_password (string): Specifies the password of Keystone
                administrator.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_keystone called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_keystone.')
            self.validate_parameters(id=id,
                                     admin_password=admin_password)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_keystone.')
            _url_path = '/keystones/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for delete_keystone.')
            _headers = {
                'adminPassword': admin_password
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_keystone.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_keystone')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_keystone.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

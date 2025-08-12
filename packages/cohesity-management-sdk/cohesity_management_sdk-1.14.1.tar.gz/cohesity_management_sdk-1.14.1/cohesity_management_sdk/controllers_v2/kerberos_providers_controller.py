# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.kerberos_providers import KerberosProviders
from cohesity_management_sdk.models_v2.kerberos_provider import KerberosProvider
from cohesity_management_sdk.models_v2.unregister_kerberos_provider import UnregisterKerberosProvider
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class KerberosProvidersController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(KerberosProvidersController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_kerberos_providers(self,
                               realm_names=None,
                               ids=None,
                               kdc_servers=None):
        """Does a GET request to /kerberos-providers.

        Get the list of Kerberos Authentication Providers.

        Args:
            realm_names (list of string, optional): Filter by a list of realm
                names.
            ids (list of long|int, optional): Filter by a list of Kerberos
                Provider Ids.
            kdc_servers (list of string, optional): Filter by a list of KDC
                servers.

        Returns:
            KerberosProviders: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_kerberos_providers called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_kerberos_providers.')
            _url_path = '/kerberos-providers'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'realmNames': realm_names,
                'ids': ids,
                'kdcServers': kdc_servers
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_kerberos_providers.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_kerberos_providers.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_kerberos_providers')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_kerberos_providers.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, KerberosProviders.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_register_kerberos_provider(self,
                                          body):
        """Does a POST request to /kerberos-providers/register.

        Register a Kerberos Authentication Provider.

        Args:
            body (RegisterOrUpdateKerberosProviderRequest): Specifies the
                parameters to Register a Kerberos Provider.

        Returns:
            KerberosProvider: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_register_kerberos_provider called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_register_kerberos_provider.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_register_kerberos_provider.')
            _url_path = '/kerberos-providers/register'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_register_kerberos_provider.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_register_kerberos_provider.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_register_kerberos_provider')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_register_kerberos_provider.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, KerberosProvider.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_unregister_kerberos_provider(self,
                                            id,
                                            body):
        """Does a POST request to /kerberos-providers/unregister/{id}.

        Unregister a Kerberos Provider.

        Args:
            id (string): Specifies the id.
            body (UnregisterKerberosRequest): Request to unregister a Kerberos
                Provider.

        Returns:
            UnregisterKerberosProvider: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_unregister_kerberos_provider called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_unregister_kerberos_provider.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_unregister_kerberos_provider.')
            _url_path = '/kerberos-providers/unregister/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_unregister_kerberos_provider.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_unregister_kerberos_provider.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_unregister_kerberos_provider')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_unregister_kerberos_provider.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, UnregisterKerberosProvider.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_kerberos_provider_by_id(self,
                                    id):
        """Does a GET request to /kerberos-providers/{id}.

        Get the Registered Kerberos Provider by id.

        Args:
            id (string): Specifies the id which will be of the pattern
                cluster_id:clusterincarnation_id:resource_id.

        Returns:
            KerberosProvider: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_kerberos_provider_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_kerberos_provider_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_kerberos_provider_by_id.')
            _url_path = '/kerberos-providers/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_kerberos_provider_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_kerberos_provider_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_kerberos_provider_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_kerberos_provider_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, KerberosProvider.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_kerberos_provider(self,
                                 id,
                                 body):
        """Does a PUT request to /kerberos-providers/{id}.

        Update the Kerberos Provider Registration.

        Args:
            id (string): Specifies the id which will be of the pattern
                cluster_id:clusterincarnation_id:resource_id.
            body (RegisterOrUpdateKerberosProviderRequest): Request to update
                a Kerberos Provider.

        Returns:
            KerberosProvider: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_kerberos_provider called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_kerberos_provider.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_kerberos_provider.')
            _url_path = '/kerberos-providers/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_kerberos_provider.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_kerberos_provider.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_kerberos_provider')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_kerberos_provider.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, KerberosProvider.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

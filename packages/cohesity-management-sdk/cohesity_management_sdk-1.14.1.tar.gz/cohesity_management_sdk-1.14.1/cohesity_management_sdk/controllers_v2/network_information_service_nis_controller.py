# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.nis_netgroups import NisNetgroups
from cohesity_management_sdk.models_v2.nis_netgroup import NisNetgroup
from cohesity_management_sdk.models_v2.nis_providers import NisProviders
from cohesity_management_sdk.models_v2.nis_provider import NisProvider
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class NetworkInformationServiceNISController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(NetworkInformationServiceNISController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_nis_netgroups(self,
                          netgroup_names=None):
        """Does a GET request to /nis-netgroups.

        Get a list of NIS netgroups.

        Args:
            netgroup_names (list of string, optional): Filter by a list of NIS
                netgroup names.

        Returns:
            NisNetgroups: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_nis_netgroups called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_nis_netgroups.')
            _url_path = '/nis-netgroups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'netgroupNames': netgroup_names
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_nis_netgroups.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_nis_netgroups.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_nis_netgroups')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_nis_netgroups.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisNetgroups.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_nis_netgroup(self,
                            body):
        """Does a POST request to /nis-netgroups.

        Create an NIS netgroup.

        Args:
            body (NisNetgroup): Specifies the parameters to create an NIS
                netgroup.

        Returns:
            NisNetgroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_nis_netgroup called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_nis_netgroup.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_nis_netgroup.')
            _url_path = '/nis-netgroups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_nis_netgroup.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_nis_netgroup.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_nis_netgroup')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_nis_netgroup.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisNetgroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_nis_netgroup_by_name(self,
                                 name):
        """Does a GET request to /nis-netgroups/{name}.

        Get an NIS netgroup by name.

        Args:
            name (string): Specifies name of the NIS netgroup.

        Returns:
            NisNetgroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_nis_netgroup_by_name called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_nis_netgroup_by_name.')
            self.validate_parameters(name=name)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_nis_netgroup_by_name.')
            _url_path = '/nis-netgroups/{name}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'name': name
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_nis_netgroup_by_name.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_nis_netgroup_by_name.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_nis_netgroup_by_name')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_nis_netgroup_by_name.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisNetgroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_nis_netgroup_by_name(self,
                                    name,
                                    body):
        """Does a PUT request to /nis-netgroups/{name}.

        Update an NIS netgroup by name.

        Args:
            name (string): Specifies name of the NIS netgroup.
            body (NisNetgroup): Request to update the NIS netgroup.

        Returns:
            NisNetgroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_nis_netgroup_by_name called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_nis_netgroup_by_name.')
            self.validate_parameters(name=name,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_nis_netgroup_by_name.')
            _url_path = '/nis-netgroups/{name}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'name': name
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_nis_netgroup_by_name.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_nis_netgroup_by_name.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_nis_netgroup_by_name')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_nis_netgroup_by_name.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisNetgroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_nis_netgroup_by_name(self,
                                    name,
                                    body):
        """Does a DELETE request to /nis-netgroups/{name}.

        Delete an NIS netgroup by name.

        Args:
            name (string): Specifies name of the NIS netgroup.
            body (NisNetgroup): Request to delete the NIS netgroup.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_nis_netgroup_by_name called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_nis_netgroup_by_name.')
            self.validate_parameters(name=name,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_nis_netgroup_by_name.')
            _url_path = '/nis-netgroups/{name}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'name': name
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for delete_nis_netgroup_by_name.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_nis_netgroup_by_name.')
            _request = self.http_client.delete(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_nis_netgroup_by_name')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_nis_netgroup_by_name.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_nis_providers(self,
                          domain_names=None):
        """Does a GET request to /nis-providers.

        Get a list of NIS Providers.

        Args:
            domain_names (list of string, optional): Filter by a list of NIS
                domain names.

        Returns:
            NisProviders: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_nis_providers called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_nis_providers.')
            _url_path = '/nis-providers'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'domainNames': domain_names
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_nis_providers.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_nis_providers.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_nis_providers')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_nis_providers.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisProviders.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_nis_provider(self,
                            body):
        """Does a POST request to /nis-providers.

        Create an NIS Provider.

        Args:
            body (NisProvider): Specifies the parameters to create an NIS
                provider entry.

        Returns:
            NisProvider: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_nis_provider called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_nis_provider.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_nis_provider.')
            _url_path = '/nis-providers'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_nis_provider.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_nis_provider.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_nis_provider')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_nis_provider.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisProvider.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_nis_provider_by_domain_name(self,
                                        domain):
        """Does a GET request to /nis-providers/{domain}.

        Get an NIS Provider by domain name.

        Args:
            domain (string): Specifies domain of an NIS Provider.

        Returns:
            NisProvider: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_nis_provider_by_domain_name called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_nis_provider_by_domain_name.')
            self.validate_parameters(domain=domain)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_nis_provider_by_domain_name.')
            _url_path = '/nis-providers/{domain}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'domain': domain
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_nis_provider_by_domain_name.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_nis_provider_by_domain_name.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_nis_provider_by_domain_name')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_nis_provider_by_domain_name.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisProvider.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_nis_provider_by_domain_name(self,
                                           domain,
                                           body):
        """Does a PUT request to /nis-providers/{domain}.

        Update an NIS Provider by domain name.

        Args:
            domain (string): Specifies domain name of an NIS Provider.
            body (NisProvider): Request to update an NIS Provider.

        Returns:
            NisProvider: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_nis_provider_by_domain_name called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_nis_provider_by_domain_name.')
            self.validate_parameters(domain=domain,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_nis_provider_by_domain_name.')
            _url_path = '/nis-providers/{domain}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'domain': domain
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_nis_provider_by_domain_name.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_nis_provider_by_domain_name.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_nis_provider_by_domain_name')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_nis_provider_by_domain_name.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NisProvider.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_nis_provider_by_domain_name(self,
                                           domain):
        """Does a DELETE request to /nis-providers/{domain}.

        Delete an NIS Provider by domain name.

        Args:
            domain (string): Specifies domain name of an NIS Provider.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_nis_provider_by_domain_name called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_nis_provider_by_domain_name.')
            self.validate_parameters(domain=domain)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_nis_provider_by_domain_name.')
            _url_path = '/nis-providers/{domain}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'domain': domain
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_nis_provider_by_domain_name.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_nis_provider_by_domain_name.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_nis_provider_by_domain_name')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_nis_provider_by_domain_name.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
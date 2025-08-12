# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.active_directories import ActiveDirectories
from cohesity_management_sdk.models_v2.active_directory import ActiveDirectory
from cohesity_management_sdk.models_v2.domain_controllers_response import DomainControllersResponse
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class ActiveDirectoryController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(ActiveDirectoryController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_active_directory(self,
                             domain_names=None,
                             ids=None,
                             tenant_ids=None,
                             include_tenants=None):
        """Does a GET request to /active-directories.

        Get the list of Active Directories.

        Args:
            domain_names (list of string, optional): Filter by a list of
                Active Directory domain names.
            ids (list of long|int, optional): Filter by a list of Active
                Directory Ids.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Protection Groups which were created by all tenants
                which the current user has permission to see. If false, then
                only Protection Groups created by the current user will be
                returned.

        Returns:
            ActiveDirectories: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_active_directory called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_active_directory.')
            _url_path = '/active-directories'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'domainNames': domain_names,
                'ids': ids,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_active_directory.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_active_directory.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_active_directory')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_active_directory.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ActiveDirectories.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_active_directory(self,
                                body):
        """Does a POST request to /active-directories.

        Create an Active Directory.

        Args:
            body (CreateActiveDirectoryRequest): Specifies the parameters to
                create an Active Directory.

        Returns:
            ActiveDirectory: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_active_directory called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_active_directory.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_active_directory.')
            _url_path = '/active-directories'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_active_directory.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_active_directory.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_active_directory')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_active_directory.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ActiveDirectory.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_active_directory_by_id(self,
                                   id,
                                   include_centrify_zones=None,
                                   include_domain_controllers=None,
                                   include_security_principals=None,
                                   prefix=None,
                                   object_class=None):
        """Does a GET request to /active-directories/{id}.

        Get an Active Directory by id.

        Args:
            id (long|int): Specifies id of an Active Directory.
            include_centrify_zones (bool, optional): Specifies whether to
                include Centrify Zones of the Active Directory in response.
            include_domain_controllers (bool, optional): Specifies whether to
                include Domain Controllers of the Active Directory in
                response.
            include_security_principals (bool, optional): Specifies whether to
                include Security Principals of the Active Directory in
                response.
            prefix (string, optional): Specifies a prefix, only security
                principals with name or sAMAccountName having this prefix
                (ignoring cases) will be returned. This field is appliciable
                and mandatory if 'includeSecurityPrincipals' is set to true.
            object_class (list of ObjectClass1Enum, optional): Specifies a
                list of object classes, only security principals with object
                class in this list will be returned. This field is appliciable
                if 'includeSecurityPrincipals' is set to true.

        Returns:
            ActiveDirectory: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_active_directory_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_active_directory_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_active_directory_by_id.')
            _url_path = '/active-directories/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'includeCentrifyZones': include_centrify_zones,
                'includeDomainControllers': include_domain_controllers,
                'includeSecurityPrincipals': include_security_principals,
                'prefix': prefix,
                'objectClass': object_class
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_active_directory_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_active_directory_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_active_directory_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_active_directory_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ActiveDirectory.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_active_directory(self,
                                id,
                                body):
        """Does a PUT request to /active-directories/{id}.

        Update an Active Directory.

        Args:
            id (long|int): Specifies id of an Active Directory.
            body (UpdateActiveDirectoryRequest): Request to update an Active
                Directory.

        Returns:
            ActiveDirectory: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_active_directory called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_active_directory.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_active_directory.')
            _url_path = '/active-directories/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_active_directory.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_active_directory.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_active_directory')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_active_directory.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ActiveDirectory.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_active_directory(self,
                                id,
                                active_directory_admin_username,
                                active_directory_admin_password):
        """Does a DELETE request to /active-directories/{id}.

        Delete an Active Directory.

        Args:
            id (long|int): Specifies id of an Active Directory.
            active_directory_admin_username (string): Specifies the username
                of the Active Direcotry Admin.
            active_directory_admin_password (string): Specifies the password
                of the Active Direcotry Admin.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_active_directory called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_active_directory.')
            self.validate_parameters(id=id,
                                     active_directory_admin_username=active_directory_admin_username,
                                     active_directory_admin_password=active_directory_admin_password)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_active_directory.')
            _url_path = '/active-directories/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for delete_active_directory.')
            _headers = {
                'activeDirectoryAdminUsername': active_directory_admin_username,
                'activeDirectoryAdminPassword': active_directory_admin_password
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_active_directory.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_active_directory')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_active_directory.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_domain_controllers(self,
                               domain_names):
        """Does a GET request to /domain-controllers.

        Get Domain Controllers of specified domains.

        Args:
            domain_names (list of string): Specifies a list of domain names.

        Returns:
            DomainControllersResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_domain_controllers called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_domain_controllers.')
            self.validate_parameters(domain_names=domain_names)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_domain_controllers.')
            _url_path = '/domain-controllers'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'domainNames': domain_names
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_domain_controllers.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_domain_controllers.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_domain_controllers')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_domain_controllers.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DomainControllersResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

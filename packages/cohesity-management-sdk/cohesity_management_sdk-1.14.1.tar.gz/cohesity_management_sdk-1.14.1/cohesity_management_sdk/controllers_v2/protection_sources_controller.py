# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.sources import Sources
from cohesity_management_sdk.models_v2.source_attribute_filters_response_params import SourceAttributeFiltersResponseParams
from cohesity_management_sdk.models_v2.source_registrations import SourceRegistrations
from cohesity_management_sdk.models_v2.source_registration import SourceRegistration
from cohesity_management_sdk.models_v2.test_connection_response_parameters import TestConnectionResponseParameters
from cohesity_management_sdk.models_v2.vdc_catalogs import VDCCatalogs
from cohesity_management_sdk.models_v2.protection_source import ProtectionSource
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class ProtectionSourcesController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(ProtectionSourcesController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_protection_sources(self,
                               tenant_ids=None,
                               include_tenants=None):
        """Does a GET request to /data-protect/sources.

        Get a List of Protection Sources.

        Args:
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which Sources are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Sources which belong belong to all tenants which the
                current user has permission to see. If false, then only
                Sources for the current user will be returned.

        Returns:
            Sources: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_sources called.')

            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_sources.')
            _url_path = '/data-protect/sources'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                                                                        _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_protection_sources.')
            _headers = {
                'accept': 'application/json'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_sources.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_sources')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_sources.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Sources.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_source_attribute_filters(self,
                                     source_uuid,
                                     environment=None):
        """Does a GET request to /data-protect/sources/filters.

        Get a List of attribute filters for leaf entities within a a source

        Args:
            source_uuid (string): Specifies the source UUID of the parent
                entity.
            environment (Environment23Enum, optional): Specifies the
                environment type of the Protection Source.

        Returns:
            SourceAttributeFiltersResponseParams: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_source_attribute_filters called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for get_source_attribute_filters.')
            self.validate_parameters(source_uuid=source_uuid)

            # Prepare query URL
            self.logger.info('Preparing query URL for get_source_attribute_filters.')
            _url_path = '/data-protect/sources/filters'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'sourceUuid': source_uuid,
                'environment': environment
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                                                                        _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_source_attribute_filters.')
            _headers = {
                'accept': 'application/json'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_source_attribute_filters.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_source_attribute_filters')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_source_attribute_filters.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SourceAttributeFiltersResponseParams.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_source_registrations(self,
                                 tenant_ids=None,
                                 include_tenants=None):
        """Does a GET request to /data-protect/sources/registrations.

        Get the list of Protection Source registrations.

        Args:
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Registrations which were created by all tenants which
                the current user has permission to see. If false, then only
                Registrations created by the current user will be returned.

        Returns:
            SourceRegistrations: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_source_registrations called.')

            # Prepare query URL
            self.logger.info('Preparing query URL for get_source_registrations.')
            _url_path = '/data-protect/sources/registrations'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                                                                        _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_source_registrations.')
            _headers = {
                'accept': 'application/json'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_source_registrations.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_source_registrations')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_source_registrations.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SourceRegistrations.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def register_protection_source(self,
                                   body):
        """Does a POST request to /data-protect/sources/registrations.

        Register a Protection Source.

        Args:
            body (SourceRegistrationParameters): Specifies the parameters to
                register a Protection Source.

        Returns:
            SourceRegistration: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('register_protection_source called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for register_protection_source.')
            self.validate_parameters(body=body)

            # Prepare query URL
            self.logger.info('Preparing query URL for register_protection_source.')
            _url_path = '/data-protect/sources/registrations'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for register_protection_source.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for register_protection_source.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'register_protection_source')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for register_protection_source.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SourceRegistration.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_protection_source_registration(self,
                                           id):
        """Does a GET request to /data-protect/sources/registrations/{id}.

        Get a Protection Source registration.

        Args:
            id (long|int): Specifies the id of the Protection Source
                registration.

        Returns:
            SourceRegistration: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_source_registration called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for get_protection_source_registration.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_source_registration.')
            _url_path = '/data-protect/sources/registrations/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_protection_source_registration.')
            _headers = {
                'accept': 'application/json'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_source_registration.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_source_registration')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_source_registration.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SourceRegistration.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_protection_source_registration(self,
                                              id,
                                              body):
        """Does a PUT request to /data-protect/sources/registrations/{id}.

        Update Protection Source registration.

        Args:
            id (long|int): Specifies the id of the Protection Source
                registration.
            body (SourceRegistrationUpdateParameters): Specifies the
                parameters to update the registration.

        Returns:
            SourceRegistration: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_protection_source_registration called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for update_protection_source_registration.')
            self.validate_parameters(id=id,
                                     body=body)

            # Prepare query URL
            self.logger.info('Preparing query URL for update_protection_source_registration.')
            _url_path = '/data-protect/sources/registrations/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for update_protection_source_registration.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_protection_source_registration.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_protection_source_registration')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_protection_source_registration.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SourceRegistration.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def patch_protection_source_registration(self,
                                             id,
                                             body):
        """Does a PATCH request to /data-protect/sources/registrations/{id}.

        Patches a Protection Source.(Available only for Cassandra).

        Args:
            id (long|int): Specifies the id of the Protection Source
                registration.
            body (SourceRegistrationPatchParameters): Specifies the
                parameters to patch the registration.

        Returns:
            SourceRegistration: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('patch_protection_source_registration called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for '
                             'patch_protection_source_registration.')
            self.validate_parameters(id=id,
                                     body=body)

            # Prepare query URL
            self.logger.info('Preparing query URL for '
                             'patch_protection_source_registration.')
            _url_path = '/data-protect/sources/registrations/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for '
                             'patch_protection_source_registration.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for '
                             'patch_protection_source_registration.')
            _request = self.http_client.patch(_query_url, headers=_headers,
                                              parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name ='patch_protection_source_registration')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for '
                             'patch_protection_source_registration.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SourceRegistration.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise



    def delete_protection_source_registration(self,
                                              id):
        """Does a DELETE request to /data-protect/sources/registrations/{id}.

        Delete Protection Source Registration.

        Args:
            id (long|int): Specifies the ID of the Protection Source
                Registration.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_protection_source_registration called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for delete_protection_source_registration.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for delete_protection_source_registration.')
            _url_path = '/data-protect/sources/registrations/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_protection_source_registration.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_protection_source_registration.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_protection_source_registration')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_protection_source_registration.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def test_connection_protection_source(self,
                                          body):
        """Does a POST request to /data-protect/sources/test-connection.

        Test connection to a source.

        Args:
            body (TestConnectionRequestParameters): Specifies the parameters
                to test connectivity with a source.

        Returns:
            TestConnectionResponseParameters: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('test_connection_protection_source called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for test_connection_protection_source.')
            self.validate_parameters(body=body)

            # Prepare query URL
            self.logger.info('Preparing query URL for test_connection_protection_source.')
            _url_path = '/data-protect/sources/test-connection'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for test_connection_protection_source.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for test_connection_protection_source.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'test_connection_protection_source')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for test_connection_protection_source.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TestConnectionResponseParameters.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_catalogs_for_vdc(self,
                             id):
        """Does a GET request to /data-protect/sources/virtual-datacenter/{id}/catalogs.

        Get the list of catalogs associated with a VMware virtual datacenter.

        Args:
            id (long|int): Specifies the ID of the VMware virtual datacenter.

        Returns:
            VDCCatalogs: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_catalogs_for_vdc called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for get_catalogs_for_vdc.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for get_catalogs_for_vdc.')
            _url_path = '/data-protect/sources/virtual-datacenter/{id}/catalogs'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_catalogs_for_vdc.')
            _headers = {
                'accept': 'application/json'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_catalogs_for_vdc.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_catalogs_for_vdc')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_catalogs_for_vdc.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, VDCCatalogs.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def protection_source_by_id(self,
                                id):
        """Does a GET request to /data-protect/sources/{id}.

        Get a Protection Source.

        Args:
            id (long|int): Specifies the id of the Protection Source.

        Returns:
            ProtectionSource: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('protection_source_by_id called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for protection_source_by_id.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for protection_source_by_id.')
            _url_path = '/data-protect/sources/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for protection_source_by_id.')
            _headers = {
                'accept': 'application/json'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for protection_source_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'protection_source_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for protection_source_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionSource.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.protection_policy_response import ProtectionPolicyResponse
from cohesity_management_sdk.models_v2.protection_policy_2 import ProtectionPolicy2
from cohesity_management_sdk.models_v2.protection_policy_template_response import ProtectionPolicyTemplateResponse
from cohesity_management_sdk.models_v2.protection_policy import ProtectionPolicy
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class ProtectionPoliciesController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(ProtectionPoliciesController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_protection_policies(self,
                                ids=None,
                                policy_names=None,
                                tenant_ids=None,
                                include_tenants=None,
                                exclude_linked_policies=None,
                                types=None,
                                vault_ids=None):
        """Does a GET request to /data-protect/policies.

        Lists protection policies based on filtering query parameters.

        Args:
            ids (list of string, optional): Filter policies by a list of
                policy ids.
            policy_names (list of string, optional): Filter policies by a list
                of policy names.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the organizations for which objects are to be returned.
            include_tenants (bool, optional): IncludeTenantPolicies specifies
                if objects of all the organizations under the hierarchy of the
                logged in user's organization should be returned.
            exclude_linked_policies (bool, optional): If excludeLinkedPolicies
                is set to true then only local policies created on cluster
                will be returned. The result will exclude all linked policies
                created from policy templates.
            types (list of Type40Enum, optional): Types specifies the policy
                type of policies to be returned
            vault_ids (list of long|int, optional): Filter by a list of Vault ids. Policies archiving to any of the
                specified vaults will be returned.

        Returns:
            ProtectionPolicyResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_policies called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_policies.')
            _url_path = '/data-protect/policies'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'policyNames': policy_names,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'excludeLinkedPolicies': exclude_linked_policies,
                'types': types,
                'vaultIds': vault_ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_protection_policies.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_policies.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_policies')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_policies.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionPolicyResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_protection_policy(self,
                                 body):
        """Does a POST request to /data-protect/policies.

        Create the Protection Policy and returns the newly created policy
        object.

        Args:
            body (ProtectionPolicyRequest): Request to create a Protection
                Policy.

        Returns:
            ProtectionPolicy2: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_protection_policy called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_protection_policy.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_protection_policy.')
            _url_path = '/data-protect/policies'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_protection_policy.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_protection_policy.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_protection_policy')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_protection_policy.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionPolicy2.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_protection_policy_by_id(self,
                                    id):
        """Does a GET request to /data-protect/policies/{id}.

        Returns the Protection Policy details based on provided Policy Id.

        Args:
            id (string): Specifies a unique id of the Protection Policy to
                return.

        Returns:
            ProtectionPolicy2: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_policy_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_protection_policy_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_policy_by_id.')
            _url_path = '/data-protect/policies/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_protection_policy_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_policy_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_policy_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_policy_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionPolicy2.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_protection_policy(self,
                                 id,
                                 body):
        """Does a PUT request to /data-protect/policies/{id}.

        Specifies the request to update the existing Protection Policy. On
        successful update, returns the updated policy object.

        Args:
            id (string): Specifies a unique id of the Protection Policy to
                update.
            body (ProtectionPolicyRequest): Request to update a Protection
                Policy.

        Returns:
            ProtectionPolicy2: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_protection_policy called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_protection_policy.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_protection_policy.')
            _url_path = '/data-protect/policies/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_protection_policy.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_protection_policy.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_protection_policy')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_protection_policy.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionPolicy2.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_protection_policy(self,
                                 id):
        """Does a DELETE request to /data-protect/policies/{id}.

        Deletes a Protection Policy based on given policy id.

        Args:
            id (string): Specifies a unique id of the Protection Policy to
                delete.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_protection_policy called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_protection_policy.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_protection_policy.')
            _url_path = '/data-protect/policies/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_protection_policy.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_protection_policy.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_protection_policy')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_protection_policy.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_policy_templates(self,
                             ids=None,
                             policy_names=None,
                             tenant_ids=None,
                             include_tenants=None):
        """Does a GET request to /data-protect/policy-templates.

        Returns the policy templates based on the filtering parameters. If no
        parameters are specified, then all the policy templates are returned.

        Args:
            ids (list of string, optional): Filter policies by a list of
                policy template ids.
            policy_names (list of string, optional): Filter policies by a list
                of policy names.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the organizations for which objects are to be returned.
            include_tenants (bool, optional): IncludeTenantPolicies specifies
                if objects of all the organizations under the hierarchy of the
                logged in user's organization should be returned.

        Returns:
            ProtectionPolicyTemplateResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_policy_templates called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_policy_templates.')
            _url_path = '/data-protect/policy-templates'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'policyNames': policy_names,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_policy_templates.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_policy_templates.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_policy_templates')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_policy_templates.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionPolicyTemplateResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_policy_template_by_id(self,
                                  id):
        """Does a GET request to /data-protect/policy-templates/{id}.

        Returns the Policy Template corresponding to the specified Policy Id.

        Args:
            id (string): Specifies a unique id of the Policy Template to
                return.

        Returns:
            ProtectionPolicy: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_policy_template_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_policy_template_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_policy_template_by_id.')
            _url_path = '/data-protect/policy-templates/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_policy_template_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_policy_template_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_policy_template_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_policy_template_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionPolicy.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
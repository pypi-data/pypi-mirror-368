# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.alerts_summary_response import AlertsSummaryResponse
from cohesity_management_sdk.models_v2.get_view_templates_result import GetViewTemplatesResult
from cohesity_management_sdk.models_v2.template import Template
from cohesity_management_sdk.models_v2.get_nlm_locks_result import GetNlmLocksResult
from cohesity_management_sdk.models_v2.get_views_result import GetViewsResult
from cohesity_management_sdk.models_v2.qos_policies_result import QosPoliciesResult
from cohesity_management_sdk.models_v2.smb_file_opens import SmbFileOpens
from cohesity_management_sdk.models_v2.view_1 import View1
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class ViewsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(ViewsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def read_view_templates(self):
        """Does a GET request to /file-services/view-template.

        All view templates on the Cohesity Cluster are returned.
        Specifying parameters filters the results that are returned.

        Returns:
            GetViewTemplatesResult: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('read_view_templates called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for read_view_templates.')
            _url_path = '/file-services/view-template'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for read_view_templates.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for read_view_templates.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'read_view_templates')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for read_view_templates.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetViewTemplatesResult.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_view_template(self,
                             body):
        """Does a POST request to /file-services/view-template.

        Create a view template.

        Args:
            body (Template): Request to create a view template.

        Returns:
            Template: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_view_template called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_view_template.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_view_template.')
            _url_path = '/file-services/view-template'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_view_template.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_view_template.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_view_template')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_view_template.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Template.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def read_view_template_by_id(self,
                                 id):
        """Does a GET request to /file-services/view-template/{id}.

        Reads a view template based on given template id."

        Args:
            id (long|int): Specifies a unique id of the view template.

        Returns:
            Template: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('read_view_template_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for read_view_template_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for read_view_template_by_id.')
            _url_path = '/file-services/view-template/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for read_view_template_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for read_view_template_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'read_view_template_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for read_view_template_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Template.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_view_template(self,
                             id,
                             body):
        """Does a PUT request to /file-services/view-template/{id}.

        Updates the view template.

        Args:
            id (long|int): Specifies a unique id of the view template.
            body (Template): Request to update a view template.

        Returns:
            Template: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_view_template called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_view_template.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_view_template.')
            _url_path = '/file-services/view-template/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_view_template.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_view_template.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_view_template')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_view_template.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Template.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_view_template(self,
                             id):
        """Does a DELETE request to /file-services/view-template/{id}.

        Deletes a view template based on given template id."

        Args:
            id (long|int): Specifies a unique id of the view template to
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
            self.logger.info('delete_view_template called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_view_template.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_view_template.')
            _url_path = '/file-services/view-template/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_view_template.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_view_template.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_view_template')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_view_template.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_views(self,
                  view_names=None,
                  view_ids=None,
                  storage_domain_ids=None,
                  storage_domain_names=None,
                  protocol_accesses=None,
                  match_partial_names=None,
                  max_count=None,
                  include_internal_views=None,
                  include_protection_groups=None,
                  max_view_id=None,
                  include_inactive=None,
                  protection_group_ids=None,
                  view_protection_group_ids=None,
                  view_count_only=None,
                  sort_by_logical_usage=None,
                  internal_access_sids=None,
                  match_alias_names=None,
                  tenant_ids=None,
                  include_tenants=None,
                  include_stats=None,
                  include_views_with_antivirus_enabled_only=None,
                  include_views_with_data_lock_enabled_only=None,
                  filer_audit_log_enabled=None):
        """Does a GET request to /file-services/views.

        If no parameters are specified, all Views on the Cohesity Cluster are
        returned.
        Specifying parameters filters the results that are returned.
        NOTE: If maxCount is set and the number of Views returned exceeds the
        maxCount,
        there are more Views to return.
        To get the next set of Views, send another request and specify the id
        of the
        last View returned in viewList from the previous response.

        Args:
            view_names (list of string, optional): Filter by a list of View
                names.
            view_ids (list of long|int, optional): Filter by a list of View
                ids.
            storage_domain_ids (list of long|int, optional): Filter by a list
                of Storage Domains (View Boxes) specified by id.
            storage_domain_names (list of string, optional): Filter by a list
                of View Box names.
            protocol_accesses (list of ProtocolAccessEnum, optional): Filter
                by a list of protocol accesses. Only views with protocol
                accesses in these specified accesses list will be returned.
            match_partial_names (bool, optional): If true, the names in
                viewNames are matched by any partial rather than exactly
                matched.
            max_count (int, optional): Specifies a limit on the number of
                Views returned.
            include_internal_views (bool, optional): Specifies if internal
                Views created by the Cohesity Cluster are also returned. In
                addition, regular Views are returned.
            include_protection_groups (bool, optional): Specifies if
                Protection Groups information needs to be returned along with
                view metadata. By default, if not set or set to true, Group
                information is returned.
            max_view_id (long|int, optional): If the number of Views to return
                exceeds the maxCount specified in the original request,
                specify the id of the last View from the viewList in the
                previous response to get the next set of Views.
            include_inactive (bool, optional): Specifies if inactive Views on
                this Remote Cluster (which have Snapshots copied by
                replication) should also be returned. Inactive Views are not
                counted towards the maxCount. By default, this field is set to
                false.
            protection_group_ids (list of long|int, optional): This field will
                be deprecated. Filter by Protection Group ids.
                Return Views that are being protected by listed Groups, which
                are specified by ids.
                If both protectionGroupIds and viewProtectionGroupIds are
                specified, only viewProtectionGroupIds will be used.
            view_protection_group_ids (list of string, optional): Filter by
                Protection Group ids. Return Views that are being protected by
                listed Groups, which are specified by ids.
            view_count_only (bool, optional): Whether to get just the total
                number of views with the given input filters. If the flag is
                true, we ignore the parameter 'maxViews' for the count. Also,
                if flag is true, list of views will not be returned. hidden:
                true
            sort_by_logical_usage (bool, optional): If set to true, the list
                is sorted descending by logical usage.
            internal_access_sids (list of string, optional): Sids of
                restricted principals who can access the view. This is an
                internal field and therefore does not have json tag. hidden:
                true
            match_alias_names (bool, optional): If true, view aliases are also
                matched with the names in viewNames.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): IncludeTenants specifies if
                objects of all the tenants under the hierarchy of the logged
                in user's organization should be returned.
            include_stats (bool, optional): If set to true, stats of views
                will be returned. By default this parameter is set to false.
            include_views_with_antivirus_enabled_only (bool, optional): If set
                to true, the list will contain only the views for which
                antivirus scan is enabled.
            include_views_with_data_lock_enabled_only (bool, optional): If set
                to true, the list will contain only the views for which either
                file level data lock is enabled or view level data lock is
                enabled.
            filer_audit_log_enabled (bool, optional): If set to true, only
                views with filer audit log enabled will be returned. If set to
                false, only views with filer audit log disabled will be
                returned.

        Returns:
            GetViewsResult: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_views called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_views.')
            _url_path = '/file-services/views'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'viewNames': view_names,
                'viewIds': view_ids,
                'storageDomainIds': storage_domain_ids,
                'storageDomainNames': storage_domain_names,
                'protocolAccesses': protocol_accesses,
                'matchPartialNames': match_partial_names,
                'maxCount': max_count,
                'includeInternalViews': include_internal_views,
                'includeProtectionGroups': include_protection_groups,
                'maxViewId': max_view_id,
                'includeInactive': include_inactive,
                'protectionGroupIds': protection_group_ids,
                'viewProtectionGroupIds': view_protection_group_ids,
                'viewCountOnly': view_count_only,
                'sortByLogicalUsage': sort_by_logical_usage,
                'internalAccessSids': internal_access_sids,
                'matchAliasNames': match_alias_names,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'includeStats': include_stats,
                'includeViewsWithAntivirusEnabledOnly': include_views_with_antivirus_enabled_only,
                'includeViewsWithDataLockEnabledOnly': include_views_with_data_lock_enabled_only,
                'filerAuditLogEnabled': filer_audit_log_enabled
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_views.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_views.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_views')


            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_views.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetViewsResult.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_view(self,
                    body):
        """Does a POST request to /file-services/views.

        Create a View.

        Args:
            body (CreateViewRequest): Request to create a View.

        Returns:
            View1: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_view called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_view.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_view.')
            _url_path = '/file-services/views'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_view.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_view.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_view')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_view.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, View1.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_view_by_id(self,
                       id):
        """Does a GET request to /file-services/views/{id}.

        Get a View based on given view Id."

        Args:
            id (long|int): Specifies a unique id of the View to delete.

        Returns:
            View1: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_view_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_view_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_view_by_id.')
            _url_path = '/file-services/views/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_view_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_view_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_view_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_view_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, View1.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_view(self,
                    id,
                    body):
        """Does a PUT request to /file-services/views/{id}.

        Returns the updated View.

        Args:
            id (long|int): Specifies a unique id of the View to update.
            body (View1): Request to update a view.

        Returns:
            View1: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_view called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_view.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_view.')
            _url_path = '/file-services/views/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_view.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_view.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_view')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_view.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, View1.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_view(self,
                    id):
        """Does a DELETE request to /file-services/views/{id}.

        Deletes a View based on given view id."

        Args:
            id (long|int): Specifies a unique id of the View to delete.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_view called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_view.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_view.')
            _url_path = '/file-services/views/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_view.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_view.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_view')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_view.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise


    def get_nlm_locks(self,
                      file_path=None,
                      view_name=None,
                      max_count=None,
                      cookie=None):
        """Does a GET request to /file-services/nlm-locks.

        Get the list of NLM locks in the views.

        Args:
            file_path (string, optional): Specifies the filepath in the view
                relative to the root filesystem. If this field is specified,
                viewName field must also be specified.
            view_name (string, optional): Specifies the name of the View in
                which to search.
                If a view name is not specified, all the views in the Cluster
                is searched. This field is mandatory if filePath field is
                specified.
            max_count (int, optional): Specifies the maximum number of NLM
                locks to return in the response.
                By default, maxCount is set to 1000. At any given instance,
                maxCount value cannot be set to more than 1000.'
            cookie (string, optional): Specifies the pagination cookie. If
                this is set, next set of locks just after the previous
                response are returned. If this is not set, first set of NLM
                locks are returned.

        Returns:
            GetNlmLocksResult: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_nlm_locks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_nlm_locks.')
            _url_path = '/file-services/nlm-locks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'filePath': file_path,
                'viewName': view_name,
                'maxCount': max_count,
                'cookie': cookie
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_nlm_locks.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_nlm_locks.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_nlm_locks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_nlm_locks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetNlmLocksResult.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise


    def list_smb_file_opens(self,
                      file_path=None,
                      view_name=None,
                      max_count=None,
                      cookie=None):
        """Does a GET request to /file-services/smb-file-opens.

        Get the list of NLM locks in the views.

        Args:
            file_path (string, optional): Specifies the filepath in the view
                relative to the root filesystem. If this field is specified,
                viewName field must also be specified.
            view_name (string, optional): Specifies the name of the View in
                which to search.
                If a view name is not specified, all the views in the Cluster
                is searched. This field is mandatory if filePath field is
                specified.
            max_count (int, optional): Specifies the maximum number of NLM
                locks to return in the response.
                By default, maxCount is set to 1000. At any given instance,
                maxCount value cannot be set to more than 1000.'
            cookie (string, optional): Specifies the pagination cookie. If
                this is set, next set of locks just after the previous
                response are returned. If this is not set, first set of NLM
                locks are returned.

        Returns:
            SmbFileOpens: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('list_smb_file_opens called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for list_smb_file_opens.')
            _url_path = '/file-services/smb-file-opens'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'filePath': file_path,
                'viewName': view_name,
                'maxCount': max_count,
                'cookie': cookie
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for list_smb_file_opens.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for list_smb_file_opens.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'list_smb_file_opens')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for list_smb_file_opens.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SmbFileOpens.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise



    def get_qos_policies(self):
        """Does a GET request to /file-services/qos-policies.

        Get the list of QoS policies on the Cohesity cluster.

        Returns:
            QosPoliciesResult: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_qos_policies called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_qos_policies.')
            _url_path = '/file-services/qos-policies'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_qos_policies.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_qos_policies.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_qos_policies')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_qos_policies.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, QosPoliciesResult.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_shares(self,
                          name=None,
                          match_partial_name=None,
                          max_count=None,
                          tenant_ids=None,
                          states_list=None):
        """Does a GET request to /file-services/shares.

        If no parameters are specified, all shares on the Cohesity Cluster
        are returned. Specifying share name/prefix filters the results that are returned.
        NOTE: If maxCount is set and the number of Shares returned exceeds the maxCount,
        there are more Share to return. To get the next set of Views, send another
        request and specify the pagination cookie from the previous response. If maxCount
        is not specified, the first 2000 Shares.

        Args:
            name (string): Specifies the Share name.
            match_partial_name (bool): If true, the share name is matched by
                any partial rather than exactly matched.
            max_count (bool, optional): Specifies a limit on the number
                of Shares returned. If maxCount is not specified, the first
                2000 Shares.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which alerts are to be used to compute
                summary.
            states_list (list of StatesListEnum, optional): Specifies list of
                alert states to filter alerts by. If not specified, only open
                alerts will be used to get summary.

        Returns:
            AlertsSummaryResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_shares called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_shares.')
            _url_path = '/file-services/shares'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'name': name,
                'matchPartialName': match_partial_name,
                'maxCount': max_count,
                'tenantIds': tenant_ids,
                'statesList': states_list
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_shares.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_shares.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_shares')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_shares.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AlertsSummaryResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
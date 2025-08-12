# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.audit_logs import AuditLogs
from cohesity_management_sdk.models_v2.audit_logs_actions import AuditLogsActions
from cohesity_management_sdk.models_v2.audit_logs_entity_types import AuditLogsEntityTypes
from cohesity_management_sdk.models_v2.filer_audit_log_configs import FilerAuditLogConfigs
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class AuditLogController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(AuditLogController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_audit_logs(self,
                       search_string=None,
                       usernames=None,
                       domains=None,
                       entity_types=None,
                       actions=None,
                       start_time_usecs=None,
                       end_time_usecs=None,
                       tenant_ids=None,
                       include_tenants=None,
                       start_index=None,
                       count=None):
        """Does a GET request to /audit-logs.

        Get a cluster audit logs.

        Args:
            search_string (string, optional): Search audit logs by
                'entityName' or 'details'.
            usernames (list of string, optional): Specifies a list of
                usernames, only audit logs made by these users will be
                returned.
            domains (list of string, optional): Specifies a list of domains,
                only audit logs made by user in these domains will be
                returned.
            entity_types (list of EntityTypes2Enum, optional): Specifies a
                list of entity types, only audit logs containing these entity
                types will be returned.
            actions (list of Actions1Enum, optional): Specifies a list of
                actions, only audit logs containing these actions will be
                returned.
            start_time_usecs (long|int, optional): Specifies a unix timestamp
                in microseconds, only audit logs made after this time will be
                returned.
            end_time_usecs (long|int, optional): Specifies a unix timestamp in
                microseconds, only audit logs made before this time will be
                returned.
            tenant_ids (list of string, optional): Specifies a list of tenant
                ids, only audit logs made by these tenants will be returned.
            include_tenants (bool, optional): If true, the response will
                include Protection Groups which were created by all tenants
                which the current user has permission to see. If false, then
                only Protection Groups created by the current user will be
                returned.
            start_index (long|int, optional): Specifies a start index. The
                oldest logs before this index will skipped, only audit logs
                from this index will be fetched.
            count (long|int, optional): Specifies the number of indexed
                obejcts to be fetched from the specified start index.

        Returns:
            AuditLogs: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_audit_logs called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_audit_logs.')
            _url_path = '/audit-logs'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'searchString': search_string,
                'usernames': usernames,
                'domains': domains,
                'entityTypes': entity_types,
                'actions': actions,
                'startTimeUsecs': start_time_usecs,
                'endTimeUsecs': end_time_usecs,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'startIndex': start_index,
                'count': count
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_audit_logs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_audit_logs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_audit_logs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_audit_logs.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AuditLogs.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_audit_logs_actions(self):
        """Does a GET request to /audit-logs/actions.

        Get all actions of cluster audit logs.

        Returns:
            AuditLogsActions: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_audit_logs_actions called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_audit_logs_actions.')
            _url_path = '/audit-logs/actions'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_audit_logs_actions.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_audit_logs_actions.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_audit_logs_actions')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_audit_logs_actions.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AuditLogsActions.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_audit_logs_entity_types(self):
        """Does a GET request to /audit-logs/entity-types.

        Get all entity types of cluster audit logs.

        Returns:
            AuditLogsEntityTypes: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_audit_logs_entity_types called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_audit_logs_entity_types.')
            _url_path = '/audit-logs/entity-types'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_audit_logs_entity_types.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_audit_logs_entity_types.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_audit_logs_entity_types')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_audit_logs_entity_types.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AuditLogsEntityTypes.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_filer_audit_log_configs(self):
        """Does a GET request to /audit-logs/filer-configs.

        Get filer audit log configs.

        Returns:
            FilerAuditLogConfigs: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_filer_audit_log_configs called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_filer_audit_log_configs.')
            _url_path = '/audit-logs/filer-configs'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_filer_audit_log_configs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_filer_audit_log_configs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_filer_audit_log_configs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_filer_audit_log_configs.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, FilerAuditLogConfigs.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_filer_audit_log_configs(self,
                                       body):
        """Does a PUT request to /audit-logs/filer-configs.

        Update filer audit log configs.

        Args:
            body (FilerAuditLogConfigs): Specifies the filer audit log config
                to update.

        Returns:
            FilerAuditLogConfigs: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_filer_audit_log_configs called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_filer_audit_log_configs.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_filer_audit_log_configs.')
            _url_path = '/audit-logs/filer-configs'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_filer_audit_log_configs.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_filer_audit_log_configs.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_filer_audit_log_configs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_filer_audit_log_configs.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, FilerAuditLogConfigs.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

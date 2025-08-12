# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.search_indexed_objects_response_body import SearchIndexedObjectsResponseBody
from cohesity_management_sdk.models_v2.protected_objects_search_result import ProtectedObjectsSearchResult
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class SearchController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(SearchController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def search_indexed_objects(self,
                               body):
        """Does a POST request to /data-protect/search/indexed-objects.

        List all the indexed objects like files and folders, emails, mailboxes
        etc., from protected objects.

        Args:
            body (SearchIndexedObjectsRequestParams): Specifies the parameters
                to search for indexed objects.

        Returns:
            SearchIndexedObjectsResponseBody: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('search_indexed_objects called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for search_indexed_objects.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for search_indexed_objects.')
            _url_path = '/data-protect/search/indexed-objects'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for search_indexed_objects.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for search_indexed_objects.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'search_indexed_objects')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for search_indexed_objects.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SearchIndexedObjectsResponseBody.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def search_protected_objects(self,
                                 search_string=None,
                                 environments=None,
                                 snapshot_actions=None,
                                 tenant_ids=None,
                                 include_tenants=None,
                                 protection_group_ids=None,
                                 object_ids=None,
                                 storage_domain_ids=None,
                                 filter_snapshot_from_usecs=None,
                                 filter_snapshot_to_usecs=None,
                                 os_types=None,
                                 source_ids=None):
        """Does a GET request to /data-protect/search/protected-objects.

        List Protected Objects.

        Args:
            search_string (string, optional): Specifies the search string to
                filter the objects. This search string will be applicable for
                objectnames and Protection Group names. User can specify a
                wildcard character '*' as a suffix to a string where all
                object and their Protection Group names are matched with the
                prefix string. For example, if vm1 and vm2 are the names of
                objects, user can specify vm* to list the objects. If not
                specified, then all the objects with Protection Groups will be
                returned which will match other filtering criteria.
            environments (list of Environment20Enum, optional): Specifies the
                environment type to filter objects.
            snapshot_actions (list of SnapshotActions2Enum, optional):
                Specifies a list of recovery actions. Only snapshots that
                applies to these actions will be returned.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Objects which belongs to all tenants which the current
                user has permission to see.
            protection_group_ids (list of string, optional): Specifies a list
                of Protection Group ids to filter the objects. If specified,
                the objects protected by specified Protection Group ids will
                be returned.
            object_ids (list of long|int, optional): Specifies a list of
                Object ids to filter.
            storage_domain_ids (list of long|int, optional): Specifies the
                Storage Domain ids to filter objects for which Protection
                Groups are writing data to Cohesity Views on the specified
                Storage Domains.
            filter_snapshot_from_usecs (long|int, optional): Specifies the
                timestamp in Unix time epoch in microseconds to filter the
                objects if the Object has a successful snapshot after this
                value.
            filter_snapshot_to_usecs (long|int, optional): Specifies the
                timestamp in Unix time epoch in microseconds to filter the
                objects if the Object has a successful snapshot before this
                value.
            os_types (list of OsType1Enum, optional): Specifies the operating
                system types to filter objects on.
            source_ids (list of long|int, optional): Specifies a list of
                Protection Source object ids to filter the objects. If
                specified, the object which are present in those Sources will
                be returned.

        Returns:
            ProtectedObjectsSearchResult: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('search_protected_objects called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for search_protected_objects.')
            _url_path = '/data-protect/search/protected-objects'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'searchString': search_string,
                'environments': environments,
                'snapshotActions': snapshot_actions,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'protectionGroupIds': protection_group_ids,
                'objectIds': object_ids,
                'storageDomainIds': storage_domain_ids,
                'filterSnapshotFromUsecs': filter_snapshot_from_usecs,
                'filterSnapshotToUsecs': filter_snapshot_to_usecs,
                'osTypes': os_types,
                'sourceIds': source_ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for search_protected_objects.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for search_protected_objects.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'search_protected_objects')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for search_protected_objects.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectedObjectsSearchResult.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

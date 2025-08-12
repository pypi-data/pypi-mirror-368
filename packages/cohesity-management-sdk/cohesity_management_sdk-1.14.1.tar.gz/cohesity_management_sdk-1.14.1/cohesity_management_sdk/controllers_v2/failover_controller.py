# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.failover_runs_response import FailoverRunsResponse
from cohesity_management_sdk.models_v2.get_view_failover_response_body import GetViewFailoverResponseBody
from cohesity_management_sdk.models_v2.failover import Failover
from cohesity_management_sdk.models_v2.init_failover_response import InitFailoverResponse
from cohesity_management_sdk.models_v2.replication_backup_activation_result import ReplicationBackupActivationResult
from cohesity_management_sdk.models_v2.failover_create_run_response import FailoverCreateRunResponse
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class FailoverController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(FailoverController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_poll_planned_runs(self,
                              failover_ids,
                              tenant_ids=None,
                              include_tenants=None):
        """Does a GET request to /data-protect/failover/pollPlannedRuns.

        Poll to see whether planned run has been scheduled or not.

        Args:
            failover_ids (list of string): Get runs for specific failover
                workflows.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Protection Groups which were created by all tenants
                which the current user has permission to see. If false, then
                only Protection Groups created by the current user will be
                returned.

        Returns:
            FailoverRunsResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_poll_planned_runs called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_poll_planned_runs.')
            self.validate_parameters(failover_ids=failover_ids)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_poll_planned_runs.')
            _url_path = '/data-protect/failover/pollPlannedRuns'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'failoverIds': failover_ids,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_poll_planned_runs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_poll_planned_runs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_poll_planned_runs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_poll_planned_runs.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, FailoverRunsResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_view_failover(self,
                          id):
        """Does a GET request to /data-protect/failover/views/{id}.

        Get failover tasks of a View.

        Args:
            id (long|int): Specifies a view id to create an failover task.

        Returns:
            GetViewFailoverResponseBody: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_view_failover called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_view_failover.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_view_failover.')
            _url_path = '/data-protect/failover/views/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_view_failover.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_view_failover.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_view_failover')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_view_failover.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetViewFailoverResponseBody.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_view_failover(self,
                             id,
                             body):
        """Does a POST request to /data-protect/failover/views/{id}.

        Create a view failover task.

        Args:
            id (long|int): Specifies a view id to create an failover task.
            body (CreateViewFailoverRequest): Specifies the request body to
                create failover task.

        Returns:
            Failover: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_view_failover called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_view_failover.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_view_failover.')
            _url_path = '/data-protect/failover/views/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_view_failover.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_view_failover.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_view_failover')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_view_failover.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Failover.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_cancel_view_failover(self,
                                    id):
        """Does a POST request to /data-protect/failover/views/{id}/cancel.

        Cancel an in progress view failover task.

        Args:
            id (long|int): Specifies a view id to cancel it's failover.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_cancel_view_failover called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_cancel_view_failover.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_cancel_view_failover.')
            _url_path = '/data-protect/failover/views/{id}/cancel'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for create_cancel_view_failover.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_cancel_view_failover.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_cancel_view_failover')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_cancel_view_failover.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_init_failover(self,
                             id,
                             body):
        """Does a POST request to /data-protect/failover/{id}.

        Initiate a failover request.

        Args:
            id (string): Specifies the id of the failover workflow.
            body (InitFailoverRequest): Specifies the parameters to initiate a
                failover. This failover request should be intiaited from
                replication cluster.

        Returns:
            InitFailoverResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_init_failover called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_init_failover.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_init_failover.')
            _url_path = '/data-protect/failover/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_init_failover.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_init_failover.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_init_failover')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_init_failover.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, InitFailoverResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_replication_backup_activation(self,
                                             id,
                                             body):
        """Does a POST request to /data-protect/failover/{id}/backupActivation.

        Specifies the configuration required for activating backup for
        failover objects on replication cluster. Here orchastrator can call
        this API multiple times as long as full set of object are
        non-overlapping. They can also use the existing job if its compatible
        to backup failover objects.

        Args:
            id (string): Specifies the id of the failover workflow.
            body (ReplicationBackupActivation): Specifies the paramteres to
                activate the backup of failover entities.

        Returns:
            ReplicationBackupActivationResult: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_replication_backup_activation called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_replication_backup_activation.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_replication_backup_activation.')
            _url_path = '/data-protect/failover/{id}/backupActivation'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_replication_backup_activation.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_replication_backup_activation.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_replication_backup_activation')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_replication_backup_activation.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ReplicationBackupActivationResult.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_source_backup_deactivation(self,
                                          id,
                                          body):
        """Does a POST request to /data-protect/failover/{id}/backupDeactivation.

        Specifies the configuration required for deactivating backup for
        failover entities on source cluster.

        Args:
            id (string): Specifies the id of the failover workflow.
            body (SourceBackupDeactivation): Specifies the paramteres to
                deactivate the backup of failover entities.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_source_backup_deactivation called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_source_backup_deactivation.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_source_backup_deactivation.')
            _url_path = '/data-protect/failover/{id}/backupDeactivation'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_source_backup_deactivation.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_source_backup_deactivation.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_source_backup_deactivation')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_source_backup_deactivation.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_cancel_failover(self,
                               id):
        """Does a POST request to /data-protect/failover/{id}/cancel.

        Specifies the request to cancel failover workflow. The cancellation
        request should not be made if '/backupActivation' or
        '/backupDeactivaetion' are already called on replication or source
        cluster respectively.

        Args:
            id (string): Specifies the id of the failover workflow.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_cancel_failover called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_cancel_failover.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_cancel_failover.')
            _url_path = '/data-protect/failover/{id}/cancel'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for create_cancel_failover.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_cancel_failover.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_cancel_failover')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_cancel_failover.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_object_linkage(self,
                              id,
                              body):
        """Does a POST request to /data-protect/failover/{id}/objectLinkage.

        Specifies the request to link failover objects on replication cluster
        to the replicated entity from source cluster. This linking need to be
        done after perforing recoveries for failed entities on replication
        cluster. This linkage will be useful when merging snapshots of object
        across replications and failovers.

        Args:
            id (string): Specifies the id of the failover workflow.
            body (ObjectLinkingRequest): Specifies the paramteres to create
                links between replicated objects and failover objects.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_object_linkage called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_object_linkage.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_object_linkage.')
            _url_path = '/data-protect/failover/{id}/objectLinkage'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_object_linkage.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_object_linkage.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_object_linkage')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_object_linkage.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_planned_run(self,
                           id,
                           body):
        """Does a POST request to /data-protect/failover/{id}/plannedRun.

        Specifies the configuration required for executing a special run as a
        part of failover workflow. This special run is triggered during
        palnned failover to sync the source cluster to replication cluster
        with minimum possible delta.

        Args:
            id (string): Specifies the id of the failover workflow.
            body (FailoverRunConfiguration): Specifies the paramteres to
                create a planned run while failover workflow.

        Returns:
            FailoverCreateRunResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_planned_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_planned_run.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_planned_run.')
            _url_path = '/data-protect/failover/{id}/plannedRun'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_planned_run.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_planned_run.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_planned_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_planned_run.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, FailoverCreateRunResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
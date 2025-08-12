# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.data_migration_source_analysis_groups import DataMigrationSourceAnalysisGroups
from cohesity_management_sdk.models_v2.common_data_migration_source_analysis_group_params import DataMigrationSourceAnalysisGroup
from cohesity_management_sdk.models_v2.specifies_the_summary_of_the_state_updation_for_the_multiple_data_migration_source_analysis_groups import SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataMigrationSourceAnalysisGroups
from cohesity_management_sdk.models_v2.data_migration_task import DataMigrationTask
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class DataMigrationController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(DataMigrationController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_data_migration_source_analysis_groups(self):
        """Does a GET request to /data-migrations/analysis-groups.

        Get the list of Data Migration source analysis groups.

        Returns:
            DataMigrationSourceAnalysisGroups: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_migration_source_analysis_groups called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_migration_source_analysis_groups.')
            _url_path = '/data-migrations/analysis-groups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_data_migration_source_analysis_groups.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_migration_source_analysis_groups.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_migration_source_analysis_groups')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_migration_source_analysis_groups.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataMigrationSourceAnalysisGroups.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_data_migration_source_analysis_group(self,
                                                    body):
        """Does a POST request to /data-migrations/analysis-groups.

        Create a source analysis group.

        Args:
            body (CommonDataMigrationSourceAnalysisGroupParams): Specifies the
                Data Migration source analysis group.

        Returns:
            DataMigrationSourceAnalysisGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_data_migration_source_analysis_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_data_migration_source_analysis_group.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_data_migration_source_analysis_group.')
            _url_path = '/data-migrations/analysis-groups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_data_migration_source_analysis_group.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_data_migration_source_analysis_group.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_data_migration_source_analysis_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_data_migration_source_analysis_group.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataMigrationSourceAnalysisGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_data_migration_source_analysis_groups_state(self,
                                                           body):
        """Does a POST request to /data-migrations/analysis-groups/states.

        Perform actions like pause or resume on the Data Migration source
        analysis groups for the specified sources.

        Args:
            body (UpdateStateOfTheDataMigrationSourceAnalysisGroups):
                Specifies the parameters to perform an action of list of Data
                Migration source analysis groups.

        Returns:
            SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataMigrationSou
                rceAnalysisGroups: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_data_migration_source_analysis_groups_state called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_data_migration_source_analysis_groups_state.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_data_migration_source_analysis_groups_state.')
            _url_path = '/data-migrations/analysis-groups/states'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_data_migration_source_analysis_groups_state.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_data_migration_source_analysis_groups_state.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_data_migration_source_analysis_groups_state')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_data_migration_source_analysis_groups_state.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataMigrationSourceAnalysisGroups.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_data_migration_source_analysis_group_by_id(self,
                                                       id):
        """Does a GET request to /data-migrations/analysis-groups/{id}.

        Returns the Data Migration source analysis group corresponding to the
        specified id.

        Args:
            id (string): Specifies a unique id of the Data Migration source
                analysis group.

        Returns:
            DataMigrationSourceAnalysisGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_migration_source_analysis_group_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_data_migration_source_analysis_group_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_migration_source_analysis_group_by_id.')
            _url_path = '/data-migrations/analysis-groups/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_data_migration_source_analysis_group_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_migration_source_analysis_group_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_migration_source_analysis_group_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_migration_source_analysis_group_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataMigrationSourceAnalysisGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_data_migration_source_analysis_group(self,
                                                    id):
        """Does a DELETE request to /data-migrations/analysis-groups/{id}.

        Returns Success if the Data Migration source analysis group is
        deleted.

        Args:
            id (string): Specifies a unique id of the Data Migration source
                analysis group.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_data_migration_source_analysis_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_data_migration_source_analysis_group.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_data_migration_source_analysis_group.')
            _url_path = '/data-migrations/analysis-groups/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_data_migration_source_analysis_group.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_data_migration_source_analysis_group.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_data_migration_source_analysis_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_data_migration_source_analysis_group.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_data_migration_tasks(self,
                                 names=None,
                                 tenant_ids=None,
                                 include_tenants=None):
        """Does a GET request to /data-migrations/tasks.

        Get the list of Data Migration Tasks.

        Args:
            names (list of string, optional): Filter by a list of Data
                Migration Task names.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenant's for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Data Migration Tasks which were created by all tenants
                which the current user has permission. If false, then only
                Data Migration Tasks created by the current user will be
                returned.

        Returns:
            list of DataMigrationTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_migration_tasks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_migration_tasks.')
            _url_path = '/data-migrations/tasks'
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
            self.logger.info('Preparing headers for get_data_migration_tasks.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_migration_tasks.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_migration_tasks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_migration_tasks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataMigrationTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_data_migration_task(self,
                                   body):
        """Does a POST request to /data-migrations/tasks.

        Create a Data Migration Task.

        Args:
            body (CommonDataMigrationTaskParams): Specifies the parameters to
                create a Data Migration Task.

        Returns:
            DataMigrationTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_data_migration_task called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_data_migration_task.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_data_migration_task.')
            _url_path = '/data-migrations/tasks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_data_migration_task.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_data_migration_task.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_data_migration_task')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_data_migration_task.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataMigrationTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_data_migration_task_by_id(self,
                                      id):
        """Does a GET request to /data-migrations/tasks/{id}.

        Return the Data Migration Task corresponding to the specified task
        ID.

        Args:
            id (string): Specifies the ID of the Data Migration Task.

        Returns:
            DataMigrationTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_migration_task_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_data_migration_task_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_migration_task_by_id.')
            _url_path = '/data-migrations/tasks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_data_migration_task_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_migration_task_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_migration_task_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_migration_task_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataMigrationTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_data_migration_task(self,
                                   id,
                                   body):
        """Does a PUT request to /data-migrations/tasks/{id}.

        Update a Data Migration Task.

        Args:
            id (string): Specifies the ID of the Data Migration Task.
            body (CommonDataMigrationTaskParams): Specifies the parameters to
                update a Data Migration Task.

        Returns:
            DataMigrationTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_data_migration_task called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_data_migration_task.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_data_migration_task.')
            _url_path = '/data-migrations/tasks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_data_migration_task.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_data_migration_task.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_data_migration_task')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_data_migration_task.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataMigrationTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_data_migration_task(self,
                                   id):
        """Does a DELETE request to /data-migrations/tasks/{id}.

        Delete the Data Migration task.

        Args:
            id (string): Specifies the ID of the Data Migration Task.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_data_migration_task called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_data_migration_task.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_data_migration_task.')
            _url_path = '/data-migrations/tasks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_data_migration_task.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_data_migration_task.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_data_migration_task')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_data_migration_task.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
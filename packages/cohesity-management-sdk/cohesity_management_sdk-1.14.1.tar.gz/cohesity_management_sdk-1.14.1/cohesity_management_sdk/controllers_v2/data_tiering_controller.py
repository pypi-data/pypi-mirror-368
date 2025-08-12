# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.data_tiering_analysis_group import DataTieringAnalysisGroup
from cohesity_management_sdk.models_v2.specifies_the_summary_of_the_state_updation_for_the_multiple_data_tiering_groups import SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataTieringGroups
from cohesity_management_sdk.models_v2.data_tiering_tag_config import DataTieringTagConfig
from cohesity_management_sdk.models_v2.data_tiering_task import DataTieringTask
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class DataTieringController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(DataTieringController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_data_tiering_analysis_groups(self,
                                         ids=None):
        """Does a GET request to /data-tiering/analysis-groups.

        Get list of all data tiering analysis groups.

        Args:
            ids (list of string, optional): Filter by a list of Analysis Group
                IDs.

        Returns:
            list of DataTieringAnalysisGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_tiering_analysis_groups called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_tiering_analysis_groups.')
            _url_path = '/data-tiering/analysis-groups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_data_tiering_analysis_groups.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_tiering_analysis_groups.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_tiering_analysis_groups')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_tiering_analysis_groups.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringAnalysisGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_data_tiering_analysis_group(self,
                                           body):
        """Does a POST request to /data-tiering/analysis-groups.

        Create a data tiering analysis group.

        Args:
            body (CommonDataTieringAnalysisGroupParams): Specifies the data
                tiering analysis group.

        Returns:
            DataTieringAnalysisGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_data_tiering_analysis_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_data_tiering_analysis_group.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_data_tiering_analysis_group.')
            _url_path = '/data-tiering/analysis-groups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_data_tiering_analysis_group.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_data_tiering_analysis_group.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_data_tiering_analysis_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_data_tiering_analysis_group.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringAnalysisGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_data_tiering_analysis_groups_state(self,
                                                  body):
        """Does a POST request to /data-tiering/analysis-groups/states.

        Perform actions like pause or resume on the data tiering analysis
        groups for the specified sources.

        Args:
            body (UpdateStateOfTheDataTieringGroups): Specifies the parameters
                to perform an action of list of data tiering analysis groups.

        Returns:
            SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataTieringGroup
                s: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_data_tiering_analysis_groups_state called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_data_tiering_analysis_groups_state.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_data_tiering_analysis_groups_state.')
            _url_path = '/data-tiering/analysis-groups/states'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_data_tiering_analysis_groups_state.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_data_tiering_analysis_groups_state.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_data_tiering_analysis_groups_state')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_data_tiering_analysis_groups_state.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataTieringGroups.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_data_tiering_analysis_group_by_id(self,
                                              id):
        """Does a GET request to /data-tiering/analysis-groups/{id}.

        Get data tiering analysis group by id.

        Args:
            id (string): Specifies a unique id of the data tiering analysis
                group.

        Returns:
            DataTieringAnalysisGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_tiering_analysis_group_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_data_tiering_analysis_group_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_tiering_analysis_group_by_id.')
            _url_path = '/data-tiering/analysis-groups/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_data_tiering_analysis_group_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_tiering_analysis_group_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_tiering_analysis_group_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_tiering_analysis_group_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringAnalysisGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_data_tiering_analysis_group(self,
                                           id):
        """Does a DELETE request to /data-tiering/analysis-groups/{id}.

        Returns NoContentResponse if the data tiering analysis group is
        deleted.

        Args:
            id (string): Specifies a unique id of the data tiering analysis
                group.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_data_tiering_analysis_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_data_tiering_analysis_group.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_data_tiering_analysis_group.')
            _url_path = '/data-tiering/analysis-groups/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_data_tiering_analysis_group.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_data_tiering_analysis_group.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_data_tiering_analysis_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_data_tiering_analysis_group.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_data_tiering_analysis_group_tags_config(self,
                                                       id,
                                                       body):
        """Does a PUT request to /data-tiering/analysis-groups/{id}/config.

        Update data tiering analysis group config.

        Args:
            id (string): Specifies a unique id of the data tiering analysis
                group.
            body (DataTieringTagConfig): Specifies the data tiering analysis
                Tags Config.

        Returns:
            DataTieringTagConfig: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_data_tiering_analysis_group_tags_config called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_data_tiering_analysis_group_tags_config.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_data_tiering_analysis_group_tags_config.')
            _url_path = '/data-tiering/analysis-groups/{id}/config'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_data_tiering_analysis_group_tags_config.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_data_tiering_analysis_group_tags_config.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_data_tiering_analysis_group_tags_config')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_data_tiering_analysis_group_tags_config.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringTagConfig.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_data_tiering_analysis_group_run(self,
                                               id):
        """Does a POST request to /data-tiering/analysis-groups/{id}/runs.

        Create a data tiering analysis group run.

        Args:
            id (string): Specifies the id of the data tiering analysis group.

        Returns:
            void: Response from the API. Request Accepted

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_data_tiering_analysis_group_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_data_tiering_analysis_group_run.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_data_tiering_analysis_group_run.')
            _url_path = '/data-tiering/analysis-groups/{id}/runs'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for create_data_tiering_analysis_group_run.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_data_tiering_analysis_group_run.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_data_tiering_analysis_group_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_data_tiering_analysis_group_run.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_cancel_data_tiering_analysis_group_run(self,
                                                      id,
                                                      run_id):
        """Does a POST request to /data-tiering/analysis-groups/{id}/runs/{runId}/cancel.

        Cancel data tiering analysis run for given analysis group ID
        and run ID

        Args:
            id (string): Specifies a unique id of data tiering group.
            run_id (string): Specifies a unique run id of data tiering group
                run.

        Returns:
            void: Response from the API. Request Accepted

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_cancel_data_tiering_analysis_group_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_cancel_data_tiering_analysis_group_run.')
            self.validate_parameters(id=id,
                                     run_id=run_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_cancel_data_tiering_analysis_group_run.')
            _url_path = '/data-tiering/analysis-groups/{id}/runs/{runId}/cancel'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id,
                'runId': run_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for create_cancel_data_tiering_analysis_group_run.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_cancel_data_tiering_analysis_group_run.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_cancel_data_tiering_analysis_group_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_cancel_data_tiering_analysis_group_run.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_data_tiering_tasks(self,
                               ids=None):
        """Does a GET request to /data-tiering/tasks.

        Get the list of data tiering tasks.

        Args:
            ids (list of string, optional): Filter by a list of data tiering
                task ids.

        Returns:
            list of DataTieringTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_tiering_tasks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_tiering_tasks.')
            _url_path = '/data-tiering/tasks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_data_tiering_tasks.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_tiering_tasks.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_tiering_tasks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_tiering_tasks.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_data_tiering_task(self,
                                 body):
        """Does a POST request to /data-tiering/tasks.

        Create a data tiering task.

        Args:
            body (CreateOrUpdateDataTieringTaskRequest): Specifies the
                parameters to create a data tiering task.

        Returns:
            DataTieringTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_data_tiering_task called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_data_tiering_task.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_data_tiering_task.')
            _url_path = '/data-tiering/tasks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_data_tiering_task.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_data_tiering_task.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_data_tiering_task')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_data_tiering_task.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_data_tiering_tasks_state(self,
                                        body):
        """Does a POST request to /data-tiering/tasks/states.

        Perform actions like pause or resume on the data tiering tasks.

        Args:
            body (UpdateStateOfTheDataTieringGroups): Specifies the parameters
                to perform an action of list of data tiering tasks.

        Returns:
            SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataTieringGroup
                s: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_data_tiering_tasks_state called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_data_tiering_tasks_state.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_data_tiering_tasks_state.')
            _url_path = '/data-tiering/tasks/states'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_data_tiering_tasks_state.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_data_tiering_tasks_state.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_data_tiering_tasks_state')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_data_tiering_tasks_state.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataTieringGroups.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_data_tiering_task_by_id(self,
                                    id):
        """Does a GET request to /data-tiering/tasks/{id}.

        Get data tiering task by id.

        Args:
            id (string): Specifies the id of the data tiering task.

        Returns:
            DataTieringTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_data_tiering_task_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_data_tiering_task_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_data_tiering_task_by_id.')
            _url_path = '/data-tiering/tasks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_data_tiering_task_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_data_tiering_task_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_data_tiering_task_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_data_tiering_task_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_data_tiering_task(self,
                                 id,
                                 body):
        """Does a PUT request to /data-tiering/tasks/{id}.

        Update a data tiering task.

        Args:
            id (string): Specifies the id of the data tiering task.
            body (CreateOrUpdateDataTieringTaskRequest): Specifies the
                parameters to update a data tiering task.

        Returns:
            DataTieringTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_data_tiering_task called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_data_tiering_task.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_data_tiering_task.')
            _url_path = '/data-tiering/tasks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_data_tiering_task.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_data_tiering_task.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_data_tiering_task')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_data_tiering_task.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, DataTieringTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_data_tiering_task(self,
                                 id):
        """Does a DELETE request to /data-tiering/tasks/{id}.

        Returns Success if the data tiering task is deleted.

        Args:
            id (string): Specifies the id of the data tiering task.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_data_tiering_task called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_data_tiering_task.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_data_tiering_task.')
            _url_path = '/data-tiering/tasks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_data_tiering_task.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_data_tiering_task.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_data_tiering_task')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_data_tiering_task.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_data_tiering_task_run(self,
                                     id,
                                     body=None):
        """Does a POST request to /data-tiering/tasks/{id}/runs.

        Create a data tiering tasks run.

        Args:
            id (string): Specifies the id of the data tiering tasks.
            body (RunOnceDataTieringTaskRequest, optional): Specifies the
                request to run tiering task once.

        Returns:
            void: Response from the API. Request Accepted

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_data_tiering_task_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_data_tiering_task_run.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_data_tiering_task_run.')
            _url_path = '/data-tiering/tasks/{id}/runs'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_data_tiering_task_run.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_data_tiering_task_run.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_data_tiering_task_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_data_tiering_task_run.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_cancel_data_tiering_task_run(self,
                                            id,
                                            run_id):
        """Does a POST request to /data-tiering/tasks/{id}/runs/{runId}/cancel.

        Cancel data tiering task run for given data tiering task id and run
        id.

        Args:
            id (string): Specifies a unique id of data tiering task.
            run_id (string): Specifies a unique run id of data tiering task.

        Returns:
            void: Response from the API. Request Accepted

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_cancel_data_tiering_task_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_cancel_data_tiering_task_run.')
            self.validate_parameters(id=id,
                                     run_id=run_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_cancel_data_tiering_task_run.')
            _url_path = '/data-tiering/tasks/{id}/runs/{runId}/cancel'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id,
                'runId': run_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for create_cancel_data_tiering_task_run.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_cancel_data_tiering_task_run.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_cancel_data_tiering_task_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_cancel_data_tiering_task_run.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
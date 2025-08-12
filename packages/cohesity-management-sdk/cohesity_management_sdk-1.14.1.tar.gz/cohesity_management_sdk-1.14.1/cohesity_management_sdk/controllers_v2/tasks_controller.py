# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.progress_tasks import ProgressTasks
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class TasksController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(TasksController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_progress_tasks(self,
                           ids=None):
        """Does a GET request to /tasks.

        Get details about tasks by providing task ids.

        Args:
            ids (list of string, optional): Specifies a unique task id to get
                the deatils of a task. To fetch the status of multiple tasks,
                pass comma seperated list of taskIds.

        Returns:
            ProgressTasks: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_progress_tasks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_progress_tasks.')
            _url_path = '/tasks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_progress_tasks.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_progress_tasks.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_progress_tasks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_progress_tasks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProgressTasks.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.tdm_objects import TdmObjects
from cohesity_management_sdk.models_v2.tdm_object import TdmObject
from cohesity_management_sdk.models_v2.tdm_object_timeline_events import TdmObjectTimelineEvents
from cohesity_management_sdk.models_v2.tdm_snapshot import TdmSnapshot
from cohesity_management_sdk.models_v2.tdm_tasks import TdmTasks
from cohesity_management_sdk.models_v2.tdm_task import TdmTask
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class TestDataManagementController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(TestDataManagementController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_tdm_objects(self,
                        ids=None,
                        environments=None,
                        name=None,
                        task_ids=None,
                        statuses=None):
        """Does a GET request to /tdm/objects.

        Get all TDM objects matching specified optional filter criteria.

        Args:
            ids (list of string, optional): Get the objects matching specifies
                IDs.
            environments (list of Environment24Enum, optional): Get the
                objects matching specified environments.
            name (string, optional): Get the objects matching specified name.
            task_ids (list of string, optional): Get the objects belonging to
                the specified TDM task IDs.
            statuses (list of Status19Enum, optional): Get the objects
                matching specified statuses.

        Returns:
            TdmObjects: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tdm_objects called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tdm_objects.')
            _url_path = '/tdm/objects'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'environments': environments,
                'name': name,
                'taskIds': task_ids,
                'statuses': statuses
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tdm_objects.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tdm_objects.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tdm_objects')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tdm_objects.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TdmObjects.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_tdm_object_by_id(self,
                             id):
        """Does a GET request to /tdm/objects/{id}.

        Get a TDM object by specifying its ID.

        Args:
            id (string): Specifies the ID of the TDM object.

        Returns:
            TdmObject: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tdm_object_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_tdm_object_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tdm_object_by_id.')
            _url_path = '/tdm/objects/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tdm_object_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tdm_object_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tdm_object_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tdm_object_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TdmObject.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_tdm_timeline_events_by_object_id(self,
                                             id,
                                             created_after=None,
                                             created_before=None):
        """Does a GET request to /tdm/objects/{id}/timeline-events.

        Get the collection of timeline events of a TDM object by specifying
        its ID.

        Args:
            id (string): Specifies the ID of the TDM object.
            created_after (long|int, optional): Get the events created after
                the specified time (in usecs from epoch).
            created_before (long|int, optional): Get the events created before
                the specified time (in usecs from epoch).

        Returns:
            TdmObjectTimelineEvents: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tdm_timeline_events_by_object_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_tdm_timeline_events_by_object_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tdm_timeline_events_by_object_id.')
            _url_path = '/tdm/objects/{id}/timeline-events'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'createdAfter': created_after,
                'createdBefore': created_before
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tdm_timeline_events_by_object_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tdm_timeline_events_by_object_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tdm_timeline_events_by_object_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tdm_timeline_events_by_object_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TdmObjectTimelineEvents.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_tdm_snapshot_by_id(self,
                                  id,
                                  body):
        """Does a PUT request to /tdm/snapshots/{id}.

        Update the details of a snapshot by specifying its ID.

        Args:
            id (string): Specifies the ID of the snapshot.
            body (CommonTdmCloneSnapshotParams): Specifies the parameters to
                update the snapshot.

        Returns:
            TdmSnapshot: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_tdm_snapshot_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_tdm_snapshot_by_id.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_tdm_snapshot_by_id.')
            _url_path = '/tdm/snapshots/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_tdm_snapshot_by_id.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_tdm_snapshot_by_id.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_tdm_snapshot_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_tdm_snapshot_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TdmSnapshot.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_tdm_snapshot_by_id(self,
                                  id):
        """Does a DELETE request to /tdm/snapshots/{id}.

        Delete a snapshot by specifying its ID.

        Args:
            id (string): Specifies the ID of the snapshot.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_tdm_snapshot_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_tdm_snapshot_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_tdm_snapshot_by_id.')
            _url_path = '/tdm/snapshots/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_tdm_snapshot_by_id.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_tdm_snapshot_by_id.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_tdm_snapshot_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_tdm_snapshot_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_tdm_tasks(self,
                      ids=None,
                      actions=None,
                      environments=None,
                      created_after_usecs=None,
                      created_before_usecs=None,
                      statuses=None,
                      object_ids=None):
        """Does a GET request to /tdm/tasks.

        Get all the TDM tasks matching specified optional filter criteria.

        Args:
            ids (list of string, optional): Get the tasks matching specified
                IDs.
            actions (list of Actions2Enum, optional): Get the tasks matching
                specified actions.
            environments (list of Environment24Enum, optional): Get the tasks
                matching specified environments.
            created_after_usecs (long|int, optional): Get the tasks created
                after the specified time (in usecs from epoch).
            created_before_usecs (long|int, optional): Get the tasks created
                before the specified time (in usecs from epoch).
            statuses (list of Status19Enum, optional): Get the tasks matching
                specified statuses.
            object_ids (list of string, optional): Get the tasks for the
                specified TDM object IDs.

        Returns:
            TdmTasks: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tdm_tasks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tdm_tasks.')
            _url_path = '/tdm/tasks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'actions': actions,
                'environments': environments,
                'createdAfterUsecs': created_after_usecs,
                'createdBeforeUsecs': created_before_usecs,
                'statuses': statuses,
                'objectIds': object_ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tdm_tasks.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tdm_tasks.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tdm_tasks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tdm_tasks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TdmTasks.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_tdm_task(self,
                        body):
        """Does a POST request to /tdm/tasks.

        Create a task for the Test Data Management (TDM) workflow.

        Args:
            body (CreateTdmTaskRequest): Specifies the parameters to create a
                TDM task.

        Returns:
            TdmTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_tdm_task called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_tdm_task.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_tdm_task.')
            _url_path = '/tdm/tasks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_tdm_task.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_tdm_task.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_tdm_task')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_tdm_task.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TdmTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_tdm_task_by_id(self,
                           id):
        """Does a GET request to /tdm/tasks/{id}.

        Get a TDM task by ID.

        Args:
            id (string): Specifies the ID of the TDM task.

        Returns:
            TdmTask: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tdm_task_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_tdm_task_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tdm_task_by_id.')
            _url_path = '/tdm/tasks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tdm_task_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tdm_task_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tdm_task_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tdm_task_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TdmTask.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
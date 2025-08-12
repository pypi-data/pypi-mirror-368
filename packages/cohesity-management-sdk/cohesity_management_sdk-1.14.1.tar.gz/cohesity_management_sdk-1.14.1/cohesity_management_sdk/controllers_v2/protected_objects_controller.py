# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.create_protected_objects_response import CreateProtectedObjectsResponse
from cohesity_management_sdk.models_v2.protected_object_action_response import ProtectedObjectActionResponse
from cohesity_management_sdk.models_v2.get_protected_object_response import GetProtectedObjectResponse
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class ProtectedObjectsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(ProtectedObjectsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def create_protect_objects_of_any_type(self,
                                           body):
        """Does a POST request to /data-protect/protected-objects.

        Create Protect Objects Backup.

        Args:
            body (CreateProtectedObjectsRequest): Specifies the parameters to
                protect objects.

        Returns:
            CreateProtectedObjectsResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_protect_objects_of_any_type called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_protect_objects_of_any_type.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_protect_objects_of_any_type.')
            _url_path = '/data-protect/protected-objects'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_protect_objects_of_any_type.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_protect_objects_of_any_type.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_protect_objects_of_any_type')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_protect_objects_of_any_type.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CreateProtectedObjectsResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_perform_action_on_protect_objects(self,
                                                 body):
        """Does a POST request to /data-protect/protected-objects/actions.

        Perform actions on Protected Objects.

        Args:
            body (ProtectdObjectsActionRequest): Specifies the parameters to
                perform an action on an already protected object.

        Returns:
            ProtectedObjectActionResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_perform_action_on_protect_objects called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_perform_action_on_protect_objects.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_perform_action_on_protect_objects.')
            _url_path = '/data-protect/protected-objects/actions'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_perform_action_on_protect_objects.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_perform_action_on_protect_objects.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_perform_action_on_protect_objects')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_perform_action_on_protect_objects.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectedObjectActionResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_protected_objects_of_any_type(self,
                                             id,
                                             body):
        """Does a PUT request to /data-protect/protected-objects/{id}.

        Update Protected object backup configuration given a object id.

        Args:
            id (long|int): Specifies the id of the Protected Object.
            body (UpdateProtectedObjectsRequest): Specifies the parameters to
                perform an update on protected objects.

        Returns:
            GetProtectedObjectResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_protected_objects_of_any_type called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_protected_objects_of_any_type.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_protected_objects_of_any_type.')
            _url_path = '/data-protect/protected-objects/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_protected_objects_of_any_type.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_protected_objects_of_any_type.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_protected_objects_of_any_type')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_protected_objects_of_any_type.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetProtectedObjectResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

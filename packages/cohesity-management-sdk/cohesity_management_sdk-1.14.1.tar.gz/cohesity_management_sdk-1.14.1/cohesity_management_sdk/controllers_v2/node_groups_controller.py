# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.node_group_response import NodeGroupResponse
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class NodeGroupsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(NodeGroupsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_node_groups(self,
                        group_names=None,
                        group_type=None):
        """Does a GET request to /nodeGroups.

        List node groups.

        Args:
            group_names (list of string, optional): Filter node groups by a
                list of node group names.
            group_type (int, optional): Filter node groups by a node group
                type.

        Returns:
            NodeGroupResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_node_groups called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_node_groups.')
            _url_path = '/nodeGroups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'groupNames': group_names,
                'groupType': group_type
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_node_groups.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_node_groups.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_node_groups')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_node_groups.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NodeGroupResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_node_group(self,
                          body):
        """Does a POST request to /nodeGroups.

        Create the Node Group and returns the newly created node group
        object.

        Args:
            body (NodeGroupRequest): Request to create a Node Group.

        Returns:
            NodeGroupResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_node_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_node_group.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_node_group.')
            _url_path = '/nodeGroups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_node_group.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_node_group.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_node_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_node_group.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NodeGroupResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_node_group_by_name(self,
                               group_name):
        """Does a GET request to /nodeGroups/{groupName}.

        Returns Node Group for given Group Name.

        Args:
            group_name (string): Specifies a unique id of Node Group to
                return.

        Returns:
            NodeGroupResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_node_group_by_name called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_node_group_by_name.')
            self.validate_parameters(group_name=group_name)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_node_group_by_name.')
            _url_path = '/nodeGroups/{groupName}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'groupName': group_name
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_node_group_by_name.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_node_group_by_name.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_node_group_by_name')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_node_group_by_name.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NodeGroupResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_node_group(self,
                          group_name,
                          body):
        """Does a PUT request to /nodeGroups/{groupName}.

        Specifies the request to update the existing Node Group. On successful
        update, returns the updated node group object.

        Args:
            group_name (string): Specifies a unique name of the Node Group to
                update.
            body (NodeGroupRequest): Request to update a Node Group.

        Returns:
            NodeGroupResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_node_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_node_group.')
            self.validate_parameters(group_name=group_name,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_node_group.')
            _url_path = '/nodeGroups/{groupName}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'groupName': group_name
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_node_group.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_node_group.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_node_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_node_group.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, NodeGroupResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_node_group(self,
                          group_name):
        """Does a DELETE request to /nodeGroups/{groupName}.

        Deletes a Node Group based on given node group name.

        Args:
            group_name (string): Specifies a unique name of the Node Group to
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
            self.logger.info('delete_node_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_node_group.')
            self.validate_parameters(group_name=group_name)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_node_group.')
            _url_path = '/nodeGroups/{groupName}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'groupName': group_name
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_node_group.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_node_group.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_node_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_node_group.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
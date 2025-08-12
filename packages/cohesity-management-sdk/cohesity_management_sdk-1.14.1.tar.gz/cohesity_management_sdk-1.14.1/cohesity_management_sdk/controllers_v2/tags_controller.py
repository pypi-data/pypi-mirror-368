# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.tag import Tag
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class TagsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(TagsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_tags(self,
                 ids=None,
                 names=None,
                 namespaces=None,
                 tenant_ids=None,
                 include_tenants=None,
                 include_marked_for_deletion=None):
        """Does a GET request to /tags.

        If no parameters are specified, all tags are returned.
        Specifying parameters filters the results that are returned.

        Args:
            ids (list of string, optional): Filter by a list of Tag Ids. If
                Ids are mentioned all other fields will be ignored.
            names (list of string, optional): Filter by a list of Tag names.
            namespaces (list of string, optional): Filter by a list of
                Namespaces.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which tags are to be returned.
            include_tenants (bool, optional): IncludeTenants specifies if tags
                of all the tenants under the hierarchy of the logged in user's
                organization should be returned. False, by default.
            include_marked_for_deletion (bool, optional): Specifies if tags
                marked for deletion should be shown. These are tags which are
                undergoing deletion. False, by default.

        Returns:
            list of Tag: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tags called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tags.')
            _url_path = '/tags'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'names': names,
                'namespaces': namespaces,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'includeMarkedForDeletion': include_marked_for_deletion
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tags.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tags.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tags')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tags.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Tag.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_tag(self,
                   body):
        """Does a POST request to /tags.

        Creates a Tag.

        Args:
            body (Tag): Request to create a Tag.

        Returns:
            Tag: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_tag called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_tag.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_tag.')
            _url_path = '/tags'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_tag.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_tag.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_tag')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_tag.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Tag.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_tag_by_id(self,
                      id):
        """Does a GET request to /tags/{id}.

        Get Tag by id.

        Args:
            id (string): Specifies the Id of the tag.

        Returns:
            Tag: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_tag_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_tag_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_tag_by_id.')
            _url_path = '/tags/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_tag_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_tag_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_tag_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_tag_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Tag.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_tag(self,
                   id,
                   body):
        """Does a PUT request to /tags/{id}.

        Updates a Tag by id.

        Args:
            id (string): Specifies the Id of the tag.
            body (Tag): Request to update a tag.

        Returns:
            Tag: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_tag called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_tag.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_tag.')
            _url_path = '/tags/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_tag.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_tag.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_tag')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_tag.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Tag.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_tag(self,
                   id):
        """Does a DELETE request to /tags/{id}.

        Deletes a Tag by id.

        Args:
            id (string): Specifies the Id of the tag.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_tag called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_tag.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_tag.')
            _url_path = '/tags/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_tag.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_tag.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_tag')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_tag.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
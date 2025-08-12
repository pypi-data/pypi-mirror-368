# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.bifrost_connections import BifrostConnections
from cohesity_management_sdk.models_v2.bifrost_connection import BifrostConnection
from cohesity_management_sdk.models_v2.rigel_connections import RigelConnections
from cohesity_management_sdk.models_v2.rigel_connection import RigelConnection
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class ExternalConnectionController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(ExternalConnectionController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_bifrost_connection(self,
                               ids=None,
                               tenant_id=None,
                               names=None):
        """Does a GET request to /connection-bifrost.

        Get connections of Bifrost on the cluster.

        Args:
            ids (list of long|int, optional): Specifies the id of the
                connections.
            tenant_id (string, optional): Specifies the id of the tenant which
                the connection belongs to.
            names (list of string, optional): Specifies the name of the
                connections.

        Returns:
            BifrostConnections: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_bifrost_connection called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_bifrost_connection.')
            _url_path = '/connection-bifrost'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'tenantId': tenant_id,
                'names': names
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_bifrost_connection.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_bifrost_connection.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_bifrost_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_bifrost_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnections.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_bifrost_connection(self,
                                  body):
        """Does a POST request to /connection-bifrost.

        Create a connection of Bifrost on the cluster.

        Args:
            body (CreateOrUpdateBifrostConnectionRequest): Specifies the
                parameters to create a connection.

        Returns:
            BifrostConnection: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_bifrost_connection called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_bifrost_connection.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_bifrost_connection.')
            _url_path = '/connection-bifrost'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_bifrost_connection.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_bifrost_connection.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_bifrost_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_bifrost_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnection.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_bifrost_connection_by_id(self,
                                     id):
        """Does a GET request to /connection-bifrost/{id}.

        Get a connection of Bifrost by the id.

        Args:
            id (long|int): Specifies the id of the Bifrost connection.

        Returns:
            BifrostConnection: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_bifrost_connection_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_bifrost_connection_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_bifrost_connection_by_id.')
            _url_path = '/connection-bifrost/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_bifrost_connection_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_bifrost_connection_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_bifrost_connection_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_bifrost_connection_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnection.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_bifrost_connection(self,
                                  id,
                                  body):
        """Does a PUT request to /connection-bifrost/{id}.

        Update a connection of Bifrost.

        Args:
            id (long|int): Specifies the id of a Bifrost connection.
            body (CreateOrUpdateBifrostConnectionRequest): Specifies the
                parameters to update a connection.

        Returns:
            BifrostConnection: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_bifrost_connection called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_bifrost_connection.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_bifrost_connection.')
            _url_path = '/connection-bifrost/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_bifrost_connection.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_bifrost_connection.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_bifrost_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_bifrost_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnection.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_bifrost_connection(self,
                                  id):
        """Does a DELETE request to /connection-bifrost/{id}.

        Delete a connection of Bifrost.

        Args:
            id (long|int): Specifies the id of a Bifrost connection.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_bifrost_connection called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_bifrost_connection.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_bifrost_connection.')
            _url_path = '/connection-bifrost/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_bifrost_connection.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_bifrost_connection.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_bifrost_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_bifrost_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_rigel_connection(self,
                             ids=None,
                             tenant_id=None,
                             names=None):
        """Does a GET request to /connection-rigel.

        Get connections of Rigel on the cluster.

        Args:
            ids (list of long|int, optional): Specifies the id of the
                connections.
            tenant_id (string, optional): Specifies the id of the tenant which
                the connection belongs to.
            names (list of string, optional): Specifies the name of the
                connection.

        Returns:
            RigelConnections: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_rigel_connection called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_rigel_connection.')
            _url_path = '/connection-rigel'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'tenantId': tenant_id,
                'names': names
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_rigel_connection.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_rigel_connection.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_rigel_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_rigel_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnections.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_rigel_connection(self,
                                body):
        """Does a POST request to /connection-rigel.

        Create a connection of Rigel on the cluster.

        Args:
            body (CreateRigelConnectionRequest): Specifies the parameters to
                create a connection.

        Returns:
            RigelConnection: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_rigel_connection called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_rigel_connection.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_rigel_connection.')
            _url_path = '/connection-rigel'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_rigel_connection.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_rigel_connection.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_rigel_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_rigel_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnection.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_rigel_connection_by_id(self,
                                   id):
        """Does a GET request to /connection-rigel/{id}.

        Get a connection of Rigel by the id.

        Args:
            id (long|int): Specifies the id of the Rigel connection.

        Returns:
            RigelConnection: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_rigel_connection_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_rigel_connection_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_rigel_connection_by_id.')
            _url_path = '/connection-rigel/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_rigel_connection_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_rigel_connection_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_rigel_connection_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_rigel_connection_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnection.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_rigel_connection(self,
                                id,
                                body):
        """Does a PUT request to /connection-rigel/{id}.

        Update a connection of Rigel.

        Args:
            id (long|int): Specifies the id of the Rigel connection.
            body (CommonCreateOrUpdateRigelConnectionRequest): Specifies the
                parameters to update the connection.

        Returns:
            RigelConnection: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_rigel_connection called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_rigel_connection.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_rigel_connection.')
            _url_path = '/connection-rigel/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_rigel_connection.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_rigel_connection.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_rigel_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_rigel_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnection.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_rigel_connection(self,
                                id):
        """Does a DELETE request to /connection-rigel/{id}.

        Delete a connection of Rigel.

        Args:
            id (long|int): Specifies the id of the Rigel connection.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_rigel_connection called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_rigel_connection.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_rigel_connection.')
            _url_path = '/connection-rigel/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_rigel_connection.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_rigel_connection.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_rigel_connection')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_rigel_connection.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
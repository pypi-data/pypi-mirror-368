# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.bifrost_connectors import BifrostConnectors
from cohesity_management_sdk.models_v2.bifrost_connector import BifrostConnector
from cohesity_management_sdk.models_v2.rigel_connectors import RigelConnectors
from cohesity_management_sdk.models_v2.rigel_connector import RigelConnector
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class ConnectorsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(ConnectorsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_bifrost_connector(self,
                              ids=None,
                              names=None,
                              tenant_id=None,
                              connection_id=None):
        """Does a GET request to /connector-hybrid-extender.

        Get Bifrost connectors on the cluster.

        Args:
            ids (list of long|int, optional): Specifies the id of the
                connectors.
            names (list of string, optional): Specifies the name of the
                connectors.
            tenant_id (string, optional): Specifies the id of the tenant which
                the connector belongs to.
            connection_id (long|int, optional): Specifies the Id of the
                connection which the connector belongs to.

        Returns:
            BifrostConnectors: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_bifrost_connector called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_bifrost_connector.')
            _url_path = '/connector-hybrid-extender'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'names': names,
                'tenantId': tenant_id,
                'connectionId': connection_id
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_bifrost_connector.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_bifrost_connector.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_bifrost_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_bifrost_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnectors.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_bifrost_connector(self,
                                 body):
        """Does a POST request to /connector-hybrid-extender.

        Create a Bifrost connector on the cluster.

        Args:
            body (CreateOrUpdateBifrostConnectorRequest): Specifies the
                parameters to create a connector.

        Returns:
            BifrostConnector: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_bifrost_connector called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_bifrost_connector.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_bifrost_connector.')
            _url_path = '/connector-hybrid-extender'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_bifrost_connector.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_bifrost_connector.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_bifrost_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_bifrost_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnector.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_bifrost_connector_by_id(self,
                                    id,
                                    tenant_id=None):
        """Does a GET request to /connector-hybrid-extender/{id}.

        Get a Bifrost connector by the id.

        Args:
            id (long|int): Specifies the id of connector.
            tenant_id (string, optional): Specifies the id of the tenant which
                the connector belongs to.

        Returns:
            BifrostConnector: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_bifrost_connector_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_bifrost_connector_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_bifrost_connector_by_id.')
            _url_path = '/connector-hybrid-extender/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'tenantId': tenant_id
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_bifrost_connector_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_bifrost_connector_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_bifrost_connector_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_bifrost_connector_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnector.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_bifrost_connector(self,
                                 id,
                                 body):
        """Does a PUT request to /connector-hybrid-extender/{id}.

        Update a Bifrost connector.

        Args:
            id (long|int): Specifies the id of connector.
            body (CreateOrUpdateBifrostConnectorRequest): Specifies the
                parameters to update a connector.

        Returns:
            BifrostConnector: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_bifrost_connector called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_bifrost_connector.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_bifrost_connector.')
            _url_path = '/connector-hybrid-extender/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_bifrost_connector.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_bifrost_connector.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_bifrost_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_bifrost_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, BifrostConnector.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_bifrost_connector(self,
                                 id):
        """Does a DELETE request to /connector-hybrid-extender/{id}.

        Delete a Bifrost connector.

        Args:
            id (long|int): Specifies the id of connector.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_bifrost_connector called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_bifrost_connector.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_bifrost_connector.')
            _url_path = '/connector-hybrid-extender/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_bitfrost_connector.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_bifrost_connector.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_bifrost_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_bifrost_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_rigel_connector(self,
                            ids=None,
                            names=None,
                            tenant_id=None,
                            connection_id=None):
        """Does a GET request to /connector-rigel.

        Get Rigel connectors on the cluster.

        Args:
            ids (list of long|int, optional): Specifies the id of the
                connector.
            names (list of string, optional): Specifies the name of the
                connectors.
            tenant_id (string, optional): Specifies the id of the tenant which
                the connector belongs to.
            connection_id (long|int, optional): Specifies the Id of the
                connection which the connector belongs to.

        Returns:
            RigelConnectors: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_rigel_connector called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_rigel_connector.')
            _url_path = '/connector-rigel'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'names': names,
                'tenantId': tenant_id,
                'connectionId': connection_id
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_rigel_connector.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_rigel_connector.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_rigel_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_rigel_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnectors.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_rigel_connector(self,
                               body):
        """Does a POST request to /connector-rigel.

        Create a Rigel connector on the cluster.

        Args:
            body (CreateRigelConnectorRequest): Specifies the parameters to
                create a connector.

        Returns:
            RigelConnector: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_rigel_connector called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_rigel_connector.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_rigel_connector.')
            _url_path = '/connector-rigel'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_rigel_connector.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_rigel_connector.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_rigel_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_rigel_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnector.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_rigel_connector_by_id(self,
                                  id,
                                  tenant_id=None):
        """Does a GET request to /connector-rigel/{id}.

        Get a Rigel connector by the id.

        Args:
            id (long|int): Specifies the id of connector.
            tenant_id (string, optional): Specifies the id of the tenant which
                the connector belongs to.

        Returns:
            RigelConnector: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_rigel_connector_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_rigel_connector_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_rigel_connector_by_id.')
            _url_path = '/connector-rigel/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'tenantId': tenant_id
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_rigel_connector_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_rigel_connector_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_rigel_connector_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_rigel_connector_by_id.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnector.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_rigel_connector(self,
                               id,
                               body):
        """Does a PUT request to /connector-rigel/{id}.

        Update a Rigel connector.

        Args:
            id (long|int): Specifies the id of connector.
            body (CommonCreateOrUpdateRigelConnectorRequest): Specifies the
                parameters to update a connector.

        Returns:
            RigelConnector: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_rigel_connector called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_rigel_connector.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_rigel_connector.')
            _url_path = '/connector-rigel/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_rigel_connector.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_rigel_connector.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_rigel_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_rigel_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelConnector.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_rigel_connector(self,
                               id,
                               body):
        """Does a DELETE request to /connector-rigel/{id}.

        Delete a Rigel connector.

        Args:
            id (long|int): Specifies the id of connector.
            body (DeleteRigelConnectorRequest): Specifies the parameters to
                delete a connector.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_rigel_connector called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_rigel_connector.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_rigel_connector.')
            _url_path = '/connector-rigel/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for delete_rigel_connector.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_rigel_connector.')
            _request = self.http_client.delete(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_rigel_connector')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_rigel_connector.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
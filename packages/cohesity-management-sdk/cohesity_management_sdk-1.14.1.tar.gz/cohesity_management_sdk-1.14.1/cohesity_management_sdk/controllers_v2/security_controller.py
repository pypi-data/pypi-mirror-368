# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.response_with_two_lists_a_list_of_enabled_ciphers_and_a_list_of_disabled_ciphers import ResponseWithTwoListsAListOfEnabledCiphersAndAListOfDisabledCiphers
from cohesity_management_sdk.models_v2.create_csr_response import CreateCSRResponse
from cohesity_management_sdk.models_v2.import_certificate_response import ImportCertificateResponse
from cohesity_management_sdk.models_v2.common_csr_response_params import CommonCsrResponseParams
from cohesity_management_sdk.models_v2.update_certificate_response import UpdateCertificateResponse
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class SecurityController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(SecurityController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_ciphers(self):
        """Does a GET request to /ciphers.

        Gets the list of ciphers enabled on the cluster.

        Returns:
            ResponseWithTwoListsAListOfEnabledCiphersAndAListOfDisabledCiphers:
                Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_ciphers called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_ciphers.')
            _url_path = '/ciphers'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_ciphers.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_ciphers.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_ciphers')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_ciphers.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ResponseWithTwoListsAListOfEnabledCiphersAndAListOfDisabledCiphers.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def modify_ciphers(self,
                       body):
        """Does a POST request to /ciphers.

        Enable/Disable a list of ciphers on the cluster.

        Args:
            body (RequestToEnableDisableAListOfCiphers): Enable/Disable
                ciphers.

        Returns:
            ResponseWithTwoListsAListOfEnabledCiphersAndAListOfDisabledCiphers:
                Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('modify_ciphers called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for modify_ciphers.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for modify_ciphers.')
            _url_path = '/ciphers'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for modify_ciphers.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for modify_ciphers.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'modify_ciphers')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for modify_ciphers.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ResponseWithTwoListsAListOfEnabledCiphersAndAListOfDisabledCiphers.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_clientcsr(self,
                         body):
        """Does a POST request to /clientcsr.

        Create two Certificate Signing Request on the cluster with the given
        details one each for client and server. Each service can have at most
        one outstanding pair of CSR.

        Args:
            body (CommonCsrRequestParams): Specifies the parameters to create
                the Certificate Signing Requests.

        Returns:
            CreateCSRResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_clientcsr called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_clientcsr.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_clientcsr.')
            _url_path = '/clientcsr'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_clientcsr.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_clientcsr.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_clientcsr')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_clientcsr.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CreateCSRResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def import_certificate_by_clientcsr(self,
                                        body):
        """Does a POST request to /clientcsr/certificate.

        Import the signed certificates on the cluster after the Certificate
        Signing Requests are created.

        Args:
            body (ImportCertificateByClientcsrRequest): Specifies the
                parameters to import the certificate.

        Returns:
            ImportCertificateResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('import_certificate_by_clientcsr called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for import_certificate_by_clientcsr.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for import_certificate_by_clientcsr.')
            _url_path = '/clientcsr/certificate'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for import_certificate_by_clientcsr.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for import_certificate_by_clientcsr.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'import_certificate_by_clientcsr')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for import_certificate_by_clientcsr.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ImportCertificateResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_csr_list(self,
                     service_name=None,
                     ids=None):
        """Does a GET request to /csr.

        List Certificate Signing Requests on the cluster with service name
        filtering.

        Args:
            service_name (ServiceName1Enum, optional): Specifies the Cohesity
                service name for which the CSR is generated. If this is not
                specified, all the csrs on the cluster will be returned.
            ids (list of string, optional): Specifies the ids of the csrs. If
                this is not specified, all the csrs on the cluster will be
                returned.

        Returns:
            list of CommonCsrResponseParams: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_csr_list called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_csr_list.')
            _url_path = '/csr'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'serviceName': service_name,
                'ids': ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_csr_list.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_csr_list.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_csr_list')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_csr_list.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CommonCsrResponseParams.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_csr(self,
                   body):
        """Does a POST request to /csr.

        Create a Certificate Signing Request on the cluster with the given
        details. Each service has at most one outstanding CSR.

        Args:
            body (CommonCsrRequestParams): Specifies the parameters to create
                a Certificate Signing Request.

        Returns:
            CommonCsrResponseParams: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_csr called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_csr.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_csr.')
            _url_path = '/csr'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_csr.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_csr.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_csr')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_csr.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CommonCsrResponseParams.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_certificate_by_csr(self,
                                  body):
        """Does a POST request to /csr/certificate.

        Update the signed certificate on the cluster after a Certificate
        Signing Request is created.

        Args:
            body (UpdateCertificateByCsrRequest): Specifies the parameters to
                update the certificate.

        Returns:
            UpdateCertificateResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_certificate_by_csr called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_certificate_by_csr.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_certificate_by_csr.')
            _url_path = '/csr/certificate'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_certificate_by_csr.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_certificate_by_csr.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_certificate_by_csr')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_certificate_by_csr.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, UpdateCertificateResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_csr_by_id(self,
                      id):
        """Does a GET request to /csr/{id}.

        List the specified Certificate Signing Request.

        Args:
            id (string): Specifies the id of the csr.

        Returns:
            CommonCsrResponseParams: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_csr_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_csr_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_csr_by_id.')
            _url_path = '/csr/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_csr_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_csr_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_csr_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_csr_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CommonCsrResponseParams.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_csr(self,
                   id):
        """Does a DELETE request to /csr/{id}.

        Delete a Certificate Signing Request on the cluster.

        Args:
            id (string): Specifies the id of the csr to be deleted.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_csr called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_csr.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_csr.')
            _url_path = '/csr/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_csr.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_csr.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_csr')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_csr.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.tenant_dmaas_certificates import TenantDmaasCertificates
from cohesity_management_sdk.models_v2.add_tenant_cert_request import AddTenantCertRequest
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class DMaaSTenantCertificateController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(DMaaSTenantCertificateController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_dmaas_tenant_certs(self,
                               tenant_ids=None):
        """Does a GET request to /dmaas-tenant-certificate.

        Get DMaaS tenant certificates on the cluster.

        Args:
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which tenants are returned. If no tenant id is
                specified, all tenant certificates are returned.

        Returns:
            TenantDmaasCertificates: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_dmaas_tenant_certs called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_dmaas_tenant_certs.')
            _url_path = '/dmaas-tenant-certificate'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'tenantIds': tenant_ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, self.config.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_dmaas_tenant_certs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_dmaas_tenant_certs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_dmaas_tenant_certs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_dmaas_tenant_certs.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, TenantDmaasCertificates.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def add_dmaas_tenant_cert(self,
                              body):
        """Does a POST request to /dmaas-tenant-certificate.

        Add a DMaaS tenant certificate to the cluster.

        Args:
            body (AddTenantCertRequest): Specifies the parameters to add the
                tenant certificate.

        Returns:
            AddTenantCertRequest: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('add_dmaas_tenant_cert called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for add_dmaas_tenant_cert.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for add_dmaas_tenant_cert.')
            _url_path = '/dmaas-tenant-certificate'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for add_dmaas_tenant_cert.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for add_dmaas_tenant_cert.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'add_dmaas_tenant_cert')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for add_dmaas_tenant_cert.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AddTenantCertRequest.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_dmaas_tenant_cert(self,
                                 tenant_id):
        """Does a DELETE request to /dmaas-tenant-certificate/{tenantId}.

        Delete a tenant certificate.

        Args:
            tenant_id (string): Specifies the id of tenant.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_dmaas_tenant_cert called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_dmaas_tenant_cert.')
            self.validate_parameters(tenant_id=tenant_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_dmaas_tenant_cert.')
            _url_path = '/dmaas-tenant-certificate/{tenantId}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'tenantId': tenant_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_dmaas_tenant_cert.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_dmaas_tenant_cert.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_dmaas_tenant_cert')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_dmaas_tenant_cert.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
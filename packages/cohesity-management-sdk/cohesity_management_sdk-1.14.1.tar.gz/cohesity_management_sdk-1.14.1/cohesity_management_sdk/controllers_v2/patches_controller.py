# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.applied_patch import AppliedPatch
from cohesity_management_sdk.models_v2.service_patch_level import ServicePatchLevel
from cohesity_management_sdk.models_v2.available_patch import AvailablePatch
from cohesity_management_sdk.models_v2.applied_patch_1 import AppliedPatch1
from cohesity_management_sdk.models_v2.patch_operation_status import PatchOperationStatus
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class PatchesController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(PatchesController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_applied_patches(self,
                            service=None,
                            include_details=None):
        """Does a GET request to /patch-management/applied-patches.

        Returns a list of currently applied patches that are running on the
        cluster.

        Args:
            service (string, optional): Specifies optional service name whose
                current patch is returned. If it is not specified, all the
                applied patches are returned.
            include_details (bool, optional): Specifies whether to return the
                details of all the fixes in the patch. By default, returns
                only the most recent fix made for the service in the patch.

        Returns:
            list of AppliedPatch: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_applied_patches called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_applied_patches.')
            _url_path = '/patch-management/applied-patches'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'service': service,
                'includeDetails': include_details
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_applied_patches.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_applied_patches.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_applied_patches')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_applied_patches.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AppliedPatch.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def revert_patches(self,
                       body):
        """Does a POST request to /patch-management/applied-patches.

        Revert an applied service patch and its dependencies.

        Args:
            body (RevertPatch): Request to revert patches.

        Returns:
            list of ServicePatchLevel: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('revert_patches called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for revert_patches.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for revert_patches.')
            _url_path = '/patch-management/applied-patches'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for revert_patches.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for revert_patches.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'revert_patches')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for revert_patches.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ServicePatchLevel.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_available_patches(self,
                              service=None,
                              include_details=None):
        """Does a GET request to /patch-management/available-patches.

        Returns a list of patches that are available and ready to apply on the
        cluster.

        Args:
            service (string, optional): Specifies optional service name whose
                available patch is returned. If it is not specified, available
                patches for all the serivces are returned.
            include_details (bool, optional): Specifies whether to return the
                description of all the fixes in the patch. By default, returns
                only the most recent fix made for the service in the patch.

        Returns:
            list of AvailablePatch: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_available_patches called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_available_patches.')
            _url_path = '/patch-management/available-patches'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'service': service,
                'includeDetails': include_details
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_available_patches.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_available_patches.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_available_patches')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_available_patches.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AvailablePatch.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def apply_patches(self,
                      body):
        """Does a POST request to /patch-management/available-patches.

        Apply a service patch and its dependencies.

        Args:
            body (ApplyPatch): Request to apply patches.

        Returns:
            list of ServicePatchLevel: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('apply_patches called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for apply_patches.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for apply_patches.')
            _url_path = '/patch-management/available-patches'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for apply_patches.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for apply_patches.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'apply_patches')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for apply_patches.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ServicePatchLevel.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_patch_operation_status(self,
                                include_details=None):
        """Does a GET request to /patch-management/operation-status.

        Returns the status of the current or the last patch operation.
        There can be only one active patch operation at any given time.

        Args:
            include_details (bool): Specifies whether to return details of
                all service patch opertions on all nodes. By default, returns
                whether there is a patch operation in progress or not.

        Returns:
            PatchOperationStatus: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_patch_operation_status called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_patch_operation_status.')
            _url_path = '/patch-management/operation-status'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'includeDetails': include_details
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_patch_operation_status.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_patch_operation_status.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_patch_operation_status')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_patch_operation_status.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, PatchOperationStatus.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise


    def get_patches_history(self):
        """Does a GET request to /patch-management/patches-history.

        Get the history of all the patch management operations.

        Returns:
            AppliedPatch1: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_patches_history called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_patches_history.')
            _url_path = '/patch-management/patches-history'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_patches_history.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_patches_history.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_patches_history')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_patches_history.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AppliedPatch1.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

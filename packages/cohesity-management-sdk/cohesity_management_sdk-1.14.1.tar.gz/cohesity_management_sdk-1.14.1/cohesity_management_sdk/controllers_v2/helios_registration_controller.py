# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.helios_registration_config import HeliosRegistrationConfig
from cohesity_management_sdk.models_v2.rigel_claim_logs import RigelClaimLogs
from cohesity_management_sdk.exceptions.error_error_exception import ErrorErrorException

class HeliosRegistrationController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None,  call_back=None):
        super(HeliosRegistrationController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def create_helios_claim(self,
                            body):
        """Does a POST request to /helios-registration.

        Claim to Helios.

        Args:
            body (RegisterToHelios): Specifies the parameters to claim to
                Helios.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_helios_claim called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_helios_claim.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_helios_claim.')
            _url_path = '/helios-registration'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_helios_claim.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_helios_claim.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_helios_claim')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_helios_claim.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_helios_reg_config(self):
        """Does a GET request to /helios-registration-config.

        Lists the Helios Registration Config.

        Returns:
            HeliosRegistrationConfig: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_helios_reg_config called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_helios_reg_config.')
            _url_path = '/helios-registration-config'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_helios_reg_config.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_helios_reg_config.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_helios_reg_config')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_helios_reg_config.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, HeliosRegistrationConfig.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_rigel_claim_logs(self):
        """Does a GET request to /rigel-claim-logs.

        Lists the logs during rigel cluster creation and claim.

        Returns:
            RigelClaimLogs: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_rigel_claim_logs called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_rigel_claim_logs.')
            _url_path = '/rigel-claim-logs'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_rigel_claim_logs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_rigel_claim_logs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_rigel_claim_logs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_rigel_claim_logs.')
            if _context.response.status_code == 0:
                raise ErrorErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RigelClaimLogs.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

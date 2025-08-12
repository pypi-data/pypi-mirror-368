# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.filtered_objects_response_body import FilteredObjectsResponseBody
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class MiscellaneousController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(MiscellaneousController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def filter_objects(self,
                       body):
        """Does a POST request to /data-protect/filter/objects.

        List all the filtered objects using given regular expressions and
        wildcard supported search strings. We are currenly supporting this for
        only SQL adapter.

        Args:
            body (FilterObjectsRequest): Specifies the parameters to filter
                objects.

        Returns:
            FilteredObjectsResponseBody: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('filter_objects called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for filter_objects.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for filter_objects.')
            _url_path = '/data-protect/filter/objects'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for filter_objects.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for filter_objects.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'filter_objects')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for filter_objects.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, FilteredObjectsResponseBody.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

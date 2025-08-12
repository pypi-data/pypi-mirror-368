# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.get_protection_runs_status_response_body import GetProtectionRunsStatusResponseBody
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class StatsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(StatsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_protection_runs_stats(self,
                                  start_time_usecs=None,
                                  end_time_usecs=None,
                                  run_status=None):
        """Does a GET request to /stats/protection-runs.

        Get statistics of protection runs.

        Args:
            start_time_usecs (long|int, optional): Specify the start time as a
                Unix epoch Timestamp (in microseconds), only runs executing
                after this time will be counted. By default it is current time
                minus a day.
            end_time_usecs (long|int, optional): Specify the end time as a
                Unix epoch Timestamp (in microseconds), only runs executing
                before this time will be counted. By default it is current
                time.
            run_status (list of RunStatus1Enum, optional): Specifies a list of
                status, runs matching the status will be returned. 'Running'
                indicates that the run is still running. 'Canceled' indicates
                that the run has been canceled. 'Failed' indicates that the
                run has failed. 'Succeeded' indicates that the run has
                finished successfully. 'SucceededWithWarning' indicates that
                the run finished successfully, but there were some warning
                messages.

        Returns:
            GetProtectionRunsStatusResponseBody: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_runs_stats called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_runs_stats.')
            _url_path = '/stats/protection-runs'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'startTimeUsecs': start_time_usecs,
                'endTimeUsecs': end_time_usecs,
                'runStatus': run_status
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_protection_runs_stats.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_runs_stats.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_runs_stats')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_runs_stats.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetProtectionRunsStatusResponseBody.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

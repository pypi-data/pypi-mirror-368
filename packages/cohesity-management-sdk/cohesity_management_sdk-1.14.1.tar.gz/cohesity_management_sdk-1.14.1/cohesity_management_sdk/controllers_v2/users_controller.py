# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.security_principals import SecurityPrincipals
from cohesity_management_sdk.models_v2.list_users_response import ListUsersResponse
from cohesity_management_sdk.models_v2.user_session_response import UserSessionResponse
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class UsersController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(UsersController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_users(self,
                  domain=None,
                  sids=None,
                  usernames=None,
                  match_partial_names=None,
                  email_addresses=None,
                  roles=None,
                  tenant_ids=None,
                  include_tenants=None
                  ):
        """Does a GET request to /users.

        If no parameters are specified, all users currently on the Cohesity
        Cluster
        are returned. Specifying parameters filters the results that are
        returned.

        Args:
            domain (string): Specifies the user domain to filter.
            sids (list of string): Specifies a list of sids to filter.
            usernames (list of string): Specifies a list of usernames to filter.
            match_partial_names (bool): If true, the names in usernames are matched by any partial rather
            than exactly matched.
            email_addresses (list of string): Specifies a list of roles to filter.
            roles (list of string): Specifies a list of roles to filter.
            tenant_ids (list of string): TenantIds contains ids of the tenants for which users are to
             be returned.
            include_tenants (bool): IncludeTenants specifies if users of all the tenants under the
          hierarchy of the logged in user's organization should be returned.

        Returns:
            list of User: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_users called.')

            # Prepare query URL
            self.logger.info('Preparing query URL for get_users.')
            _url_path = '/users'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'domain' : domain,
                'sids' : sids,
                'usernames' : usernames,
                'matchPartialNames' : match_partial_names,
                'emailAddresses' : email_addresses,
                'roles' : roles,
                'tenantIds' : tenant_ids,
                'includeTenants' : include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(
                _query_builder, _query_parameters,
                ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_users.')
            _headers = {'accept': 'application/json'}

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_users.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name='get_users')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_users.')
            if _context.response.status_code == 0 :
                raise ErrorException('Error' , _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body , ListUsersResponse.from_dictionary)


        except Exception as e:
            self.logger.error(e, exc_info=True)
            raise

    def get_security_principals(self,
                                sids):
        """Does a GET request to /security-principals.

        Get Security Principals

        Args:
            sids (list of string): Specifies a list of SIDs.

        Returns:
            SecurityPrincipals: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_security_principals called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_security_principals.')
            self.validate_parameters(sids=sids)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_security_principals.')
            _url_path = '/security-principals'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'sids': sids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_security_principals.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_security_principals.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_security_principals')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_security_principals.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SecurityPrincipals.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_session(self, body) :
        """Does a POST request to /users/sessions.

        Create a user session

        Args:
            body (CreateUserSessionRequestParams): Specifies the parameters to create
                  a user session

        Returns:
            UserSessionResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try :
            self.logger.info('create_session called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for create_session.')
            self.validate_parameters(body=body)

            # Prepare query URL
            self.logger.info('Preparing query URL for create_session.')
            _url_path = '/users/sessions'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for create_session.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_session.')
            _request = self.http_client.post(_query_url , headers=_headers , parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request , self.config)
            _context = self.execute_request(_request , name='create_session')


            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_session.')
            if _context.response.status_code == 0 :
                raise ErrorException('Error' , _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body , UserSessionResponse.from_dictionary)

        except Exception as e :
            self.logger.error(e , exc_info=True)
            raise

    def delete_session(self,sid):
        """Does a DELETE request to /users/sessions.

        Returns Success if the session is deleted.

        Args:
            sid (string): Specifies a user sid. If sid is not given system wide sessions
          are deleted.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try :
            self.logger.info('delete_session called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for delete_session.')
            self.validate_parameters(sid=sid)

            # Prepare query URL
            self.logger.info('Preparing query URL for delete_session.')
            _url_path = '/users/sessions'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'sid' : sid
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder ,
                                                                        _query_parameters ,
                                                                        ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_session.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_session.')
            _request = self.http_client.delete(_query_url , headers=_headers)
            CustomHeaderAuth.apply(_request , self.config)
            _context = self.execute_request(_request , name='delete_session')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_session.')
            if _context.response.status_code == 0 :
                raise ErrorException('Error' , _context)
            self.validate_response(_context)

        except Exception as e :
            self.logger.error(e , exc_info=True)
            raise
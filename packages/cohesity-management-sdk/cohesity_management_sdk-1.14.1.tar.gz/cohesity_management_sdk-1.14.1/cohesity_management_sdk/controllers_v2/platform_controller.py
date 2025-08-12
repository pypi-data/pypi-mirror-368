# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.alerts_summary_response import AlertsSummaryResponse
from cohesity_management_sdk.models_v2.list_of_chassis import ListOfChassis
from cohesity_management_sdk.models_v2.cluster_ui_config import ClusterUiConfig
from cohesity_management_sdk.models_v2.chassis_specific_response import ChassisSpecificResponse
from cohesity_management_sdk.models_v2.create_cluster_response import CreateClusterResponse
from cohesity_management_sdk.models_v2.remote_disks import RemoteDisks
from cohesity_management_sdk.models_v2.add_remote_disk_response_body import AddRemoteDiskResponseBody
from cohesity_management_sdk.models_v2.list_of_racks import ListOfRacks
from cohesity_management_sdk.models_v2.rack_specific_response import RackSpecificResponse
from cohesity_management_sdk.models_v2.registered_remote_storage_list import RegisteredRemoteStorageList
from cohesity_management_sdk.models_v2.remote_storage_registration_parameters import RemoteStorageRegistrationParameters
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class PlatformController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(PlatformController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_alert_summary(self,
                          start_time_usecs=None,
                          end_time_usecs=None,
                          include_tenants=None,
                          tenant_ids=None,
                          states_list=None):
        """Does a GET request to /alertsSummary.

        Get alerts summary grouped by category.

        Args:
            start_time_usecs (long|int, optional): Filter by start time.
                Specify the start time as a Unix epoch Timestamp (in
                microseconds). By default it is current time minus a day.
            end_time_usecs (long|int, optional): Filter by end time. Specify
                the end time as a Unix epoch Timestamp (in microseconds). By
                default it is current time.
            include_tenants (bool, optional): IncludeTenants specifies if
                alerts of all the tenants under the hierarchy of the logged in
                user's organization should be used to compute summary.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which alerts are to be used to compute
                summary.
            states_list (list of StatesListEnum, optional): Specifies list of
                alert states to filter alerts by. If not specified, only open
                alerts will be used to get summary.

        Returns:
            AlertsSummaryResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_alert_summary called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_alert_summary.')
            _url_path = '/alertsSummary'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'startTimeUsecs': start_time_usecs,
                'endTimeUsecs': end_time_usecs,
                'includeTenants': include_tenants,
                'tenantIds': tenant_ids,
                'statesList': states_list
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_alert_summary.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_alert_summary.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_alert_summary')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_alert_summary.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AlertsSummaryResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_chassis(self,
                    no_rack_assigned=None):
        """Does a GET request to /chassis.

        Get list of all chassis info that are part of cluster.

        Args:
            no_rack_assigned (bool, optional): Filters chassis that have no
                rack assigned.

        Returns:
            ListOfChassis: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_chassis called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_chassis.')
            _url_path = '/chassis'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'noRackAssigned': no_rack_assigned
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_chassis.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_chassis.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_chassis')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_chassis.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ListOfChassis.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_chassis_by_id(self,
                          id):
        """Does a GET request to /chassis/{id}.

        Get a chassis info by id.

        Args:
            id (long|int): Specifies the id of chassis.

        Returns:
            ChassisSpecificResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_chassis_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_chassis_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_chassis_by_id.')
            _url_path = '/chassis/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_chassis_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_chassis_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_chassis_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_chassis_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ChassisSpecificResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_chassis_by_id(self,
                             id,
                             body=None):
        """Does a PATCH request to /chassis/{id}.

        Update selected properties of chassis info by id.

        Args:
            id (long|int): Specifies the id of chassis.
            body (ChassisSpecificResponse, optional): Specifies the parameters
                to update chassis.

        Returns:
            ChassisSpecificResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_chassis_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_chassis_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_chassis_by_id.')
            _url_path = '/chassis/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_chassis_by_id.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_chassis_by_id.')
            _request = self.http_client.patch(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_chassis_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_chassis_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ChassisSpecificResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_cluster(self,
                       body):
        """Does a POST request to /clusters.

        Create a cluster with given network and cluster configuration.

        Args:
            body (CreateClusterRequestParameters): Specifies the parameters to
                create cluster.

        Returns:
            CreateClusterResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_cluster called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_cluster.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_cluster.')
            _url_path = '/clusters'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_cluster.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_cluster.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_cluster')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_cluster.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CreateClusterResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_remote_disks(self,
                         disk_ids=None,
                         node_ids=None,
                         tiers=None,
                         mount_path=None,
                         file_system=None):
        """Does a GET request to /disks/remote.

        Get remote disks.

        Args:
            disk_ids (list of long|int, optional): Specifies a list of disk
                ids, only disks having these ids will be returned.
            node_ids (list of long|int, optional): Specifies a list of node
                ids, only disks in these nodes will be returned.
            tiers (list of Tier2Enum, optional): Specifies a list of disk
                tiers, only disks with given tiers will be returned.
            mount_path (string, optional): This field is deprecated. Providing
                this queryparam will not have any impact. Please use
                fileSystem query param to filter instead.
            file_system (string, optional): Specified file system name to
                search. only disks with file system name that partially
                matches the specified name will be returned.

        Returns:
            RemoteDisks: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_remote_disks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_remote_disks.')
            _url_path = '/disks/remote'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'diskIds': disk_ids,
                'nodeIds': node_ids,
                'tiers': tiers,
                'mountPath': mount_path,
                'fileSystem': file_system
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_remote_disks.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_remote_disks.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_remote_disks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_remote_disks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RemoteDisks.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def add_remote_disk(self,
                        body):
        """Does a POST request to /disks/remote.

        Add a remote disk.

        Args:
            body (RemoteDisks): Specifies the remote disk configuration.

        Returns:
            AddRemoteDiskResponseBody: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('add_remote_disk called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for add_remote_disk.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for add_remote_disk.')
            _url_path = '/disks/remote'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for add_remote_disk.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for add_remote_disk.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'add_remote_disk')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for add_remote_disk.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, AddRemoteDiskResponseBody.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def remove_remote_disk(self,
                           id):
        """Does a DELETE request to /disks/remote/{id}.

        Remove a remote disk.

        Args:
            id (long|int): Specifies the id of the remote disk to remove.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('remove_remote_disk called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for remove_remote_disk.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for remove_remote_disk.')
            _url_path = '/disks/remote/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for remove_remote_disk.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for remove_remote_disk.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'remove_remote_disk')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for remove_remote_disk.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_racks(self):
        """Does a GET request to /racks.

        Get list of all racks that are part of cluster.

        Returns:
            ListOfRacks: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_racks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_racks.')
            _url_path = '/racks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_racks.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_racks.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_racks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_racks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ListOfRacks.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_racks(self,
                     body):
        """Does a POST request to /racks.

        Create list of racks and optionally also assign list of chassis to
        each rack

        Args:
            body (ListOfRacks): Specifies the parameters to create racks.

        Returns:
            ListOfRacks: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_racks called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_racks.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_racks.')
            _url_path = '/racks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_racks.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_racks.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_racks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_racks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ListOfRacks.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_racks(self):
        """Does a DELETE request to /racks.

        Delete all the racks.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_racks called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_racks.')
            _url_path = '/racks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_racks.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_racks.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_racks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_racks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_racks(self,
                     body):
        """Does a PATCH request to /racks.

        Updates list of racks with name, chassis list or/and location

        Args:
            body (ListOfRacks): Specifies the parameters to update racks.

        Returns:
            ListOfRacks: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_racks called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_racks.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_racks.')
            _url_path = '/racks'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_racks.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_racks.')
            _request = self.http_client.patch(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_racks')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_racks.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ListOfRacks.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_rack_by_id(self,
                       id):
        """Does a GET request to /racks/{id}.

        Get a rack info by id.

        Args:
            id (long|int): Specifies the id of rack.

        Returns:
            RackSpecificResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_rack_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_rack_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_rack_by_id.')
            _url_path = '/racks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_rack_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_rack_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_rack_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_rack_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RackSpecificResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_rack_by_id(self,
                          id):
        """Does a DELETE request to /racks/{id}.

        Delete a given rack by id.

        Args:
            id (string): Specifies a unique id of the rack.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_rack_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_rack_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_rack_by_id.')
            _url_path = '/racks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_rack_by_id.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_rack_by_id.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_rack_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_rack_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_rack_by_id(self,
                          id,
                          body=None):
        """Does a PATCH request to /racks/{id}.

        Update selected properties of a rack given by id.

        Args:
            id (long|int): Specifies the id of rack.
            body (RackSpecificResponse, optional): Specifies the parameters to
                update rack.

        Returns:
            RackSpecificResponse: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_rack_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_rack_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_rack_by_id.')
            _url_path = '/racks/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_rack_by_id.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_rack_by_id.')
            _request = self.http_client.patch(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_rack_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_rack_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RackSpecificResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_registered_remote_storage_list(self):
        """Does a GET request to /remote-storage.

        Get summary about list of registered remote storage servers.

        Returns:
            RegisteredRemoteStorageList: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_registered_remote_storage_list called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_registered_remote_storage_list.')
            _url_path = '/remote-storage'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_registered_remote_storage_list.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_registered_remote_storage_list.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_registered_remote_storage_list')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_registered_remote_storage_list.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RegisteredRemoteStorageList.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def register_new_remote_storage(self,
                                    body):
        """Does a POST request to /remote-storage.

        Register a remote storage to be used for disaggregated storage.

        Args:
            body (RemoteStorageRegistrationParameters): Specifies the
                parameters to register a remote storage management server.

        Returns:
            RemoteStorageRegistrationParameters: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('register_new_remote_storage called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for register_new_remote_storage.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for register_new_remote_storage.')
            _url_path = '/remote-storage'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for register_new_remote_storage.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for register_new_remote_storage.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'register_new_remote_storage')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for register_new_remote_storage.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RemoteStorageRegistrationParameters.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_remote_storage_details(self,
                                   id,
                                   include_available_space=False,
                                   include_available_data_vips=False):
        """Does a GET request to /remote-storage/{id}.

        Get details of remote storage given by id.

        Args:
            id (long|int): Specifies the id of the registered remote storage.
            include_available_space (bool, optional): Specifies whether to
                include available capacity on remote storage.
            include_available_data_vips (bool, optional): Specifies whether to
                include available data vips on remote storage.

        Returns:
            RemoteStorageRegistrationParameters: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_remote_storage_details called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_remote_storage_details.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_remote_storage_details.')
            _url_path = '/remote-storage/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'includeAvailableSpace': include_available_space,
                'includeAvailableDataVips': include_available_data_vips
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_remote_storage_details.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_remote_storage_details.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_remote_storage_details')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_remote_storage_details.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RemoteStorageRegistrationParameters.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_remote_storage_registration(self,
                                           id):
        """Does a DELETE request to /remote-storage/{id}.

        Delete remote storage registration.

        Args:
            id (long|int): Specifies the registration id of the registered
                remote storage.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_remote_storage_registration called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_remote_storage_registration.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_remote_storage_registration.')
            _url_path = '/remote-storage/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_remote_storage_registration.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_remote_storage_registration.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_remote_storage_registration')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_remote_storage_registration.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_remote_storage_registration(self,
                                           id,
                                           body):
        """Does a PATCH request to /remote-storage/{id}.

        Update Registered Remote Storage Config.

        Args:
            id (long|int): Specifies the registration id of the registered
                remote storage.
            body (RemoteStorageRegistrationParameters): Specifies the
                parameters to update the registration.

        Returns:
            RemoteStorageRegistrationParameters: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_remote_storage_registration called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_remote_storage_registration.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_remote_storage_registration.')
            _url_path = '/remote-storage/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_remote_storage_registration.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_remote_storage_registration.')
            _request = self.http_client.patch(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_remote_storage_registration')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_remote_storage_registration.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, RemoteStorageRegistrationParameters.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise


    def update_cluster_ui_config(self,
                             body):
        """Does a PUT request to /clusters/ui-config.

        Update customized UI config for the cluster.

        Args:
            body (ClusterUiConfig): Specifies the UI config.

        Returns:
            ClusterUiConfig: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_cluster_ui_config called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_cluster_ui_config.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_cluster_ui_config.')
            _url_path = '/clusters/ui-config'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_cluster_ui_config.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_cluster_ui_config.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_cluster_ui_config')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_cluster_ui_config.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ClusterUiConfig.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise


    def get_cluster_ui_config(self):
        """Does a GET request to /clusters/ui-config.

        Get customized UI config for the cluster.

        Returns:
            ClusterUiConfig: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_cluster_ui_config called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_cluster_ui_config.')
            _url_path = '/clusters/ui-config'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_cluster_ui_config.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_cluster_ui_config.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_cluster_ui_config')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_cluster_ui_config.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ClusterUiConfig.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
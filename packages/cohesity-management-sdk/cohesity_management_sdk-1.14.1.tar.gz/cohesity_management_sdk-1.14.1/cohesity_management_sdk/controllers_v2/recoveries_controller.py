# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.list_of_recoveries import ListOfRecoveries
from cohesity_management_sdk.models_v2.recovery import Recovery
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class RecoveriesController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(RecoveriesController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_recoveries(self,
                       ids=None,
                       tenant_ids=None,
                       include_tenants=None,
                       start_time_usecs=None,
                       end_time_usecs=None,
                       snapshot_target_type=None,
                       archival_target_type=None,
                       snapshot_environments=None,
                       status=None,
                       recovery_actions=None):
        """Does a GET request to /data-protect/recoveries.

        Lists the Recoveries.

        Args:
            ids (list of string, optional): Filter Recoveries for given ids.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the organizations for which recoveries are to be returned.
            include_tenants (bool, optional): Specifies if objects of all the
                organizations under the hierarchy of the logged in user's
                organization should be returned.
            start_time_usecs (long|int, optional): Returns the recoveries
                which are started after the specific time. This value should
                be in Unix timestamp epoch in microseconds.
            end_time_usecs (long|int, optional): Returns the recoveries which
                are started before the specific time. This value should be in
                Unix timestamp epoch in microseconds.
            snapshot_target_type (list of SnapshotTargetType2Enum, optional):
                Specifies the snapshot's target type from which recovery has
                been performed.
            archival_target_type (list of ArchivalTargetType2Enum, optional):
                Specifies the snapshot's archival target type from which
                recovery has been performed. This parameter applies only if
                'snapshotTargetType' is 'Archival'.
            snapshot_environments (list of SnapshotEnvironment2Enum,
                optional): Specifies the list of snapshot environment types to
                filter Recoveries. If empty, Recoveries related to all
                environments will be returned.
            status (list of Status18Enum, optional): Specifies the list of run
                status to filter Recoveries. If empty, Recoveries with all run
                status will be returned.
            recovery_actions (list of RecoveryAction14Enum, optional):
                Specifies the list of recovery actions to filter Recoveries.
                If empty, Recoveries related to all actions will be returned.

        Returns:
            ListOfRecoveries: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_recoveries called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_recoveries.')
            _url_path = '/data-protect/recoveries'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'startTimeUsecs': start_time_usecs,
                'endTimeUsecs': end_time_usecs,
                'snapshotTargetType': snapshot_target_type,
                'archivalTargetType': archival_target_type,
                'snapshotEnvironments': snapshot_environments,
                'status': status,
                'recoveryActions': recovery_actions
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_recoveries.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_recoveries.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_recoveries')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_recoveries.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ListOfRecoveries.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_recovery(self,
                        body):
        """Does a POST request to /data-protect/recoveries.

        Performs a Recovery.

        Args:
            body (CreateRecoveryRequestParams): Specifies the parameters to
                create a Recovery.

        Returns:
            Recovery: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_recovery called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_recovery.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_recovery.')
            _url_path = '/data-protect/recoveries'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_recovery.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_recovery.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_recovery')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_recovery.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Recovery.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_download_files_and_folders_recovery(self,
                                                   body):
        """Does a POST request to /data-protect/recoveries/downloadFilesAndFoldersRecovery.

        Creates a download files and folders recovery.

        Args:
            body (DownloadFilesAndFoldersRecoveryParams): Specifies the
                parameters to create a download files and folder recovery.

        Returns:
            Recovery: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_download_files_and_folders_recovery called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_download_files_and_folders_recovery.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_download_files_and_folders_recovery.')
            _url_path = '/data-protect/recoveries/downloadFilesAndFoldersRecovery'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_download_files_and_folders_recovery.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_download_files_and_folders_recovery.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_download_files_and_folders_recovery')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_download_files_and_folders_recovery.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Recovery.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_recovery_by_id(self,
                           id,
                           include_tenants=None):
        """Does a GET request to /data-protect/recoveries/{id}.

        Get Recovery for a given id.

        Args:
            id (string): Specifies the id of a Recovery.
            include_tenants (bool, optional): Specifies if objects of all the
                organizations under the hierarchy of the logged in user's
                organization should be returned.

        Returns:
            Recovery: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_recovery_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_recovery_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_recovery_by_id.')
            _url_path = '/data-protect/recoveries/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_recovery_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_recovery_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_recovery_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_recovery_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Recovery.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def cancel_recovery_by_id(self,
                              id):
        """Does a POST request to /data-protect/recoveries/{id}/cancel.

        Cancel Recovery for a given id.

        Args:
            id (string): Specifies the id of a Recovery.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('cancel_recovery_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for cancel_recovery_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for cancel_recovery_by_id.')
            _url_path = '/data-protect/recoveries/{id}/cancel'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for cancel_recovery_by_id.')
            _headers = {
                'accept'       : 'application/json',
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for cancel_recovery_by_id.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'cancel_recovery_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for cancel_recovery_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def download_files_from_recovery(self,
                                     id,
                                     start_offset=None,
                                     length=None,
                                     file_type=None):

        """Does a GET request to /data-protect/recoveries/{id}/downloadFiles.

        Download files from the given download file recovery.

        This shall be deprecated and will be removed in future release

        Args:
            id (string): Specifies the id of a Recovery.
            start_offset (long|int, optional): Specifies the start offset of
                file chunk to be downloaded.
            length (long|int, optional): Specifies the length of bytes to
                download. This can not be greater than 8MB (8388608 byets)
            file_type (string, optional): Specifies the downloaded type,
                i.e: error, success_files_list

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('download_files_from_recovery called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for download_files_from_recovery.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for download_files_from_recovery.')
            _url_path = '/data-protect/recoveries/{id}/downloadFiles'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'startOffset': start_offset,
                'length': length,
                'fileType': file_type
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare and execute request
            self.logger.info('Preparing and executing request for download_files_from_recovery.')
            _request = self.http_client.get(_query_url)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'download_files_from_recovery')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for download_files_from_recovery.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def download_files_from_recovery_1(self ,
                                     id ,
                                     start_offset=None ,
                                     length=None ,
                                     file_type=None,
                                     source_name=None,
                                     start_time=None,
                                     include_tenants=None) :
        """Does a GET request to /data-protect/recoveries/{id}/download-files.

        Download files from the given download file recovery.

        Args:
            id (string): Specifies the id of a Recovery.
            start_offset (long|int, optional): Specifies the start offset of
                file chunk to be downloaded.
            length (long|int, optional): Specifies the length of bytes to
                download. This can not be greater than 8MB (8388608 byets)
            file_type (string, optional): Specifies the downloaded type,
                i.e: error, success_files_list
            source_name (string): Specifies the name of the source on which restore is done
            start_time (string): Specifies the start time of restore task
            include_tenants (bool): Specifies if objects of all the organizations under the hierarchy
                of the logged in user's organization should be returned.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try :
            self.logger.info('download_files_from_recovery_1 called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for download_files_from_recovery_1.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for download_files_from_recovery_1.')
            _url_path = '/data-protect/recoveries/{id}/download-files'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path , {
                'id' : id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'startOffset' : start_offset ,
                'length'      : length ,
                'fileType'    : file_type,
                'sourceName'  : source_name,
                'startTime'   : start_time,
                'includeTenants': include_tenants
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder ,
                                                                        _query_parameters ,
                                                                        ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare and execute request
            self.logger.info('Preparing and executing request for download_files_from_recovery_1.')
            _request = self.http_client.get(_query_url)
            CustomHeaderAuth.apply(_request , self.config)
            _context = self.execute_request(_request , name='download_files_from_recovery_1')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for download_files_from_recovery_1.')
            if _context.response.status_code == 0 :
                raise ErrorException('Error' , _context)
            self.validate_response(_context)

        except Exception as e :
            self.logger.error(e , exc_info=True)
            raise



    def tear_down_recovery_by_id(self,
                                 id):
        """Does a POST request to /data-protect/recoveries/{id}/tearDown.

        Tear down Recovery for a given id.

        This shall be deprecated and will be removed in future release

        Args:
            id (string): Specifies the id of a Recovery.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('tear_down_recovery_by_id called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for tear_down_recovery_by_id.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for tear_down_recovery_by_id.')
            _url_path = '/data-protect/recoveries/{id}/tearDown'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, {
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for tear_down_recovery_by_id.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for tear_down_recovery_by_id.')
            _request = self.http_client.post(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'tear_down_recovery_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for tear_down_recovery_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def tear_down_recovery_by_id_1(self ,
                                 id) :
        """Does a POST request to /data-protect/recoveries/{id}/tear-down.

        Tear down Recovery for a given id.

        Args:
            id (string): Specifies the id of a Recovery.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try :
            self.logger.info('tear_down_recovery_by_id_1 called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for tear_down_recovery_by_id_1.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for tear_down_recovery_by_id_1.')
            _url_path = '/data-protect/recoveries/{id}/tear-down'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path , {
                'id' : id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for tear_down_recovery_by_id_1.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for tear_down_recovery_by_id_1.')
            _request = self.http_client.post(_query_url , headers=_headers)
            CustomHeaderAuth.apply(_request , self.config)
            _context = self.execute_request(_request , name='tear_down_recovery_by_id_1')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for tear_down_recovery_by_id_1.')
            if _context.response.status_code == 0 :
                raise ErrorException('Error' , _context)
            self.validate_response(_context)

        except Exception as e :
            self.logger.error(e , exc_info=True)
            raise

    def download_indexed_file(self,
                              snapshots_id,
                              file_path=None,
                              retry_attempt=None,
                              start_offset=None,
                              length=None):
        """Does a GET request to /data-protect/snapshots/{snapshotsId}/downloadFile.

        Download an indexed file from a snapshot.

        This shall be deprecated and will be removed in future release

        Args:
            snapshots_id (string): Specifies the snapshot id to download
                from.
            file_path (string, optional): Specifies the path to the file to
                download. If no path is specified and snapshot environment is
                kVMWare, VMX file for VMware will be downloaded. For other
                snapshot environments, this field must be specified.
            retry_attempt (long|int, optional): Specifies the number of
                attempts the protection run took to create this file.
            start_offset (long|int, optional): Specifies the start offset of
                file chunk to be downloaded.
            length (long|int, optional): Specifies the length of bytes to
                download. This can not be greater than 8MB (8388608 byets)

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('download_indexed_file called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for download_indexed_file.')
            self.validate_parameters(snapshots_id=snapshots_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for download_indexed_file.')
            _url_path = '/data-protect/snapshots/{snapshotsId}/downloadFile'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'snapshotsId': snapshots_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'filePath': file_path,
                'retryAttempt': retry_attempt,
                'startOffset': start_offset,
                'length': length
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for download_indexed_file.')
            _request = self.http_client.get(_query_url)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'download_indexed_file')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for download_indexed_file.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def download_indexed_file_1(self ,
                              snapshots_id ,
                              file_path=None ,
                              nvram_file=None,
                              retry_attempt=None ,
                              start_offset=None ,
                              length=None) :
        """Does a GET request to /data-protect/snapshots/{snapshotsId}/download-file.

        Download an indexed file from a snapshot.

        Args:
            snapshots_id (string): Specifies the snapshot id to download
                from.
            file_path (string, optional): Specifies the path to the file to
                download. If no path is specified and snapshot environment is
                kVMWare, VMX file for VMware will be downloaded. For other
                snapshot environments, this field must be specified.
            nvram_file (bool): Specifies if NVRAM file for VMware should be downloaded.
            retry_attempt (long|int, optional): Specifies the number of
                attempts the protection run took to create this file.
            start_offset (long|int, optional): Specifies the start offset of
                file chunk to be downloaded.
            length (long|int, optional): Specifies the length of bytes to
                download. This can not be greater than 8MB (8388608 byets)

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try :
            self.logger.info('download_indexed_file_1 called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for download_indexed_file_1.')
            self.validate_parameters(snapshots_id=snapshots_id)

            # Prepare query URL
            self.logger.info('Preparing query URL for download_indexed_file_1.')
            _url_path = '/data-protect/snapshots/{snapshotsId}/download-file'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path , {
                'snapshotsId' : snapshots_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'filePath'     : file_path ,
                'nvramFile'    : nvram_file,
                'retryAttempt' : retry_attempt ,
                'startOffset'  : start_offset ,
                'length'       : length
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder ,
                                                                        _query_parameters ,
                                                                        ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare and execute request
            self.logger.info('Preparing and executing request for download_indexed_file_1.')
            _request = self.http_client.get(_query_url)
            CustomHeaderAuth.apply(_request , self.config)
            _context = self.execute_request(_request , name='download_indexed_file_1')
            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for download_indexed_file_1.')
            if _context.response.status_code == 0 :
                raise ErrorException('Error' , _context)
            self.validate_response(_context)

        except Exception as e :
            self.logger.error(e , exc_info=True)
            raise

    def get_recovery_errors_report(self, id):
        """Does a GET request to /data-protect/recoveries/{id}/download-messages:.

        Get a CSV error report for given recovery operation. Each row in
        CSV report contains the File Path, error/warning code and error/warning
        message.

        Args:
            id (string): Specifies a unique ID of a Recovery.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_recovery_errors_report called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_recovery_errors_report.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_recovery_errors_report.')
            _url_path = '/data-protect/recoveries/{id}/download-messages:'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_recovery_errors_report.')
            _headers = { 'accept' : 'application/json' }

    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_recovery_errors_report.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_recovery_errors_report')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_recovery_errors_report.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
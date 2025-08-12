# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.objects import Objects
from cohesity_management_sdk.models_v2.object_information import Object
from cohesity_management_sdk.models_v2.object_runs import ObjectRuns
from cohesity_management_sdk.models_v2.object_snapshots import ObjectSnapshots
from cohesity_management_sdk.models_v2.object_snapshot import ObjectSnapshot
from cohesity_management_sdk.models_v2.object_information_1 import ObjectInformation1
from cohesity_management_sdk.models_v2.snapshot_diff_result import SnapshotDiffResult
from cohesity_management_sdk.models_v2.get_indexed_object_snapshots_response_body import GetIndexedObjectSnapshotsResponseBody
from cohesity_management_sdk.models_v2.common_object_snapshot_volume_params import CommonObjectSnapshotVolumeParams
from cohesity_management_sdk.models_v2.object_summaries import ObjectSummaries
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class ObjectsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(ObjectsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_objects(self,
                    environments=None,
                    tenant_ids=None,
                    include_tenants=None,
                    global_ids=None):
        """Does a GET request to /data-protect/objects.

        List objects which can be used for data protection.

        Args:
            environments (list of Environment20Enum, optional): Specifies the
                environment type to filter objects.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Objects which belongs to all tenants which the current
                user has permission to see.
            global_ids (list of string, optional): Unique id to uniquely identify an object across clusters, if
          the same object is present on multiple clusters. For example, in case of
          a replication workflow, the object could be present on both local and remote
          cluster. In such scenarios, using the globalId, information about the object
          can be collected across the clusters. This is also applicable when object
          gets mapped to another cluster during tenant migration.

        Returns:
            Objects: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_objects called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_objects.')
            _url_path = '/data-protect/objects'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'environments': environments,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'globalIds': global_ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_objects.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_objects.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_objects')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_objects.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Objects.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_object_by_id(self,
                         id,
                         only_protected_objects=None,
                         storage_domain_id=None,
                         environments=None,
                         tenant_ids=None,
                         include_tenants=None,
                         include_last_run_info=None,
                         only_auto_protected_objects=None,
                         only_leaf_objects=None):
        """Does a GET request to /data-protect/objects/{id}.

        Get an object by object id.

        Args:
            id (long|int): Specifies the id of Object.
            only_protected_objects (bool, optional):  If true, the response
                will include only objects which have been protected.
            storage_domain_id (long|int, optional): Filter by Storage Domain
                id. Only Objects protected to this Storage Domain will be
                returned.
            environments (Environment2Enum, optional): Filter by environment
                types such as 'kVMware', 'kView', etc.
                Only Protected objects protecting the specified environment
                types are returned.
            tenant_ids (list of string, optional):  TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Objects which belongs to all tenants which the current
                user has permission to see.
            include_last_run_info (bool, optional): If true, the response will
                include information about the last protection run on this
                object.
            only_auto_protected_objects (bool, None): If true, the response
                will include only the auto protected objects.
            only_leaf_objects (bool, None): If true, the response will include
                only the leaf level objects.

        Returns:
            ObjectInformation: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_object_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_object_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_object_by_id.')
            _url_path = '/data-protect/objects/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'onlyProtectedObjects': only_protected_objects,
                'storageDomainId': storage_domain_id,
                'environments': environments,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'includeLastRunInfo': include_last_run_info,
                'onlyAutoProtectedObjects': only_auto_protected_objects,
                'onlyLeafObjects': only_leaf_objects
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_object_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_object_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_object_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_object_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, Object.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def perform_action_on_object(self,
                                 id,
                                 body):
        """Does a POST request to /data-protect/objects/{id}/actions.

        Perform an action on an object. Depending on the object environment
        type, different actions are available.

        Args:
            id (long|int): Specifies the id of the Object.
            body (PeformAnActionOnAnObject): Specifies the parameters to
                perform an action on an object.

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('perform_action_on_object called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for perform_action_on_object.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for perform_action_on_object.')
            _url_path = '/data-protect/objects/{id}/actions'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for perform_action_on_object.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for perform_action_on_object.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'perform_action_on_object')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for perform_action_on_object.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_object_runs(self,
                        id,
                        run_id=None,
                        start_time_usecs=None,
                        end_time_usecs=None,
                        tenant_ids=None,
                        include_tenants=None,
                        run_types=None,
                        local_backup_object_status=None,
                        replication_object_status=None,
                        archival_object_status=None,
                        cloud_spin_run_status=None,
                        num_runs=None,
                        pagination_cookie=None,
                        exclude_non_restorable_runs=False):
        """Does a GET request to /data-protect/objects/{id}/runs.

        Get the runs for a particular object.

        Args:
            id (long|int): Specifies a unique id of the object.
            run_id (string, optional): Specifies the protection run id.
            start_time_usecs (long|int, optional): Filter by a start time.
                Specify the start time as a Unix epoch Timestamp (in
                microseconds).
            end_time_usecs (long|int, optional): Filter by a end time. Specify
                the start time as a Unix epoch Timestamp (in microseconds).
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Protection Group Runs which were created by all
                tenants which the current user has permission to see. If
                false, then only Protection Group Runs created by the current
                user will be returned.
            run_types (list of RunType5Enum, optional): Filter by run type.
                Only protection run matching the specified types will be
                returned.
            local_backup_object_status (list of LocalBackupObjectStatusEnum,
                optional): Specifies a list of status for the object in the
                backup run.
            replication_object_status (list of ReplicationObjectStatusEnum,
                optional): Specifies a list of status for the object in the
                replication run.
            archival_object_status (list of ArchivalObjectStatusEnum, optional):
                Specifies a list of status for the object in the archival run.
            cloud_spin_run_status (list of CloudSpinRunStatusEnum, optional):
                Specifies a list of status for the object in the cloud spin run.
            num_runs (long|int, optional): Specifies the max number of runs.
                If not specified, at most 100 runs will be returned.
            pagination_cookie (bool): Specifies the pagination cookie with
                which subsequent parts of the response can be fetched. Users
                can use this to get next runs
            exclude_non_restorable_runs (bool, optional): Specifies whether to
                exclude non restorable runs. Run is treated restorable only if
                there is atleast one object snapshot (which may be either a
                local or an archival snapshot) which is not deleted or
                expired. Default value is false.

        Returns:
            ObjectRuns: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_object_runs called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_object_runs.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_object_runs.')
            _url_path = '/data-protect/objects/{id}/runs'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'runId': run_id,
                'startTimeUsecs': start_time_usecs,
                'endTimeUsecs': end_time_usecs,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'runTypes': run_types,
                'localBackupRunStatus': local_backup_object_status,
                'replicationObjectStatus': replication_object_status,
                'archivalObjectStatus': archival_object_status,
                'cloudSpinRunStatus': cloud_spin_run_status,
                'numRuns': num_runs,
                'paginationCookie': pagination_cookie,
                'excludeNonRestorableRuns': exclude_non_restorable_runs
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_object_runs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_object_runs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_object_runs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_object_runs.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ObjectRuns.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_object_snapshots(self,
                             id,
                             from_time_usecs=None,
                             to_time_usecs=None,
                             run_start_from_time_usecs=None,
                             run_start_to_time_usecs=None,
                             snapshot_actions=None,
                             run_types=None,
                             run_instance_ids=None,
                             protection_group_ids=None,
                             region_ids=None,
                             object_action_keys=None):
        """Does a GET request to /data-protect/objects/{id}/snapshots.

        List the snapshots for a given object.

        Args:
            id (long|int): Specifies the id of the Object.
            from_time_usecs (long|int, optional): Specifies the timestamp in
                Unix time epoch in microseconds to filter Object's snapshots
                which are taken after this value.
            to_time_usecs (long|int, optional): Specifies the timestamp in
                Unix time epoch in microseconds to filter Object's snapshots
                which are taken before this value.
            run_start_from_time_usecs (long|int, optional): Specifies the timestamp in Unix time epoch in microseconds to
                filter Object's snapshots which were run after this value.
            run_start_to_time_usecs (long|int, optional): Specifies the timestamp in Unix time epoch in microseconds to
                filter Object's snapshots which were run before this value.
            snapshot_actions (list of string, optional): Specifies a list of recovery actions. Only snapshots that applies
                to these actions will be returned.
            run_types (list of RunType6Enum, optional): Filter by run type.
                Only protection run matching the specified types will be
                returned. By default, CDP hydration snapshots are not
                included, unless explicitly queried using this field.
            run_instance_ids (list of long|int, optional): Filter by a list
                run instance ids. If specified, only snapshots created by
                these protection runs will be returned.
            protection_group_ids (list of string, optional): If specified,
                this returns only the snapshots of the specified object ID,
                which belong to the provided protection group IDs.
            region_ids (list of string, optional): Filter by a list of region ids.
            object_action_keys (list of ObjectActionKeysEnum, optional): Filter by ObjectActionKey, which uniquely represents protection
               of an object. An object can be protected in multiple ways but atmost once
               for a given combination of ObjectActionKey. When specified, only snapshots
               matching given action keys are returned for corresponding object.

        Returns:
            ObjectSnapshots: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_object_snapshots called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_object_snapshots.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_object_snapshots.')
            _url_path = '/data-protect/objects/{id}/snapshots'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'fromTimeUsecs': from_time_usecs,
                'toTimeUsecs': to_time_usecs,
                'runStartFromTimeUsecs': run_start_from_time_usecs,
                'runStartToTimeUsecs':run_start_to_time_usecs,
                'snapshotActions':snapshot_actions,
                'runTypes': run_types,
                'runInstanceIds': run_instance_ids,
                'protectionGroupIds': protection_group_ids,
                "regionIds": region_ids,
                "objectActionKeys": object_action_keys
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_object_snapshots.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_object_snapshots.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_object_snapshots')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_object_snapshots.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ObjectSnapshots.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_object_snapshot(self,
                               id,
                               snapshot_id,
                               body):
        """Does a PUT request to /data-protect/objects/{id}/snapshots/{snapshotId}.

        Update an object snapshot.

        Args:
            id (long|int): Specifies the id of the Object.
            snapshot_id (string): Specifies the id of the snapshot.<br> Note:
                1. If the snapshotid of one of the apps is specified, it
                applies for all the databases in the Protection Run.<br> 2. In
                case of volume based jobs, please specify the snapshotid of
                the source not the database. if source snapshot is specified,
                applied to source snapshot. if database snapshotid is
                specified in case of volume based jobs, then it is applicable
                for host's snapshot.
            body (UpdateObjectSnapshotRequest): Specifies the parameters
                update an object snapshot.

        Returns:
            ObjectSnapshot: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_object_snapshot called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_object_snapshot.')
            self.validate_parameters(id=id,
                                     snapshot_id=snapshot_id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_object_snapshot.')
            _url_path = '/data-protect/objects/{id}/snapshots/{snapshotId}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id,
                'snapshotId': snapshot_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_object_snapshot.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_object_snapshot.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_object_snapshot')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_object_snapshot.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ObjectSnapshot.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_object_tree(self,
                        id):
        """Does a GET request to /data-protect/objects/{id}/tree.

        Get the objects tree hierarchy for for an Object. If the object does
        not have a hierarchy then a single object will be returned.

        Args:
            id (long|int): Specifies the id of the Object.

        Returns:
            ObjectInformation1: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_object_tree called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_object_tree.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_object_tree.')
            _url_path = '/data-protect/objects/{id}/tree'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_object_tree.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_object_tree.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_object_tree')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_object_tree.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ObjectInformation1.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_indexed_object_snapshots(self,
                                     protection_group_id,
                                     object_id,
                                     indexed_object_name,
                                     include_indexed_snapshots_only=False,
                                     from_time_usecs=None,
                                     to_time_usecs=None,
                                     run_types=None):
        """Does a GET request to /data-protect/objects/{objectId}/protection-groups/{protectionGroupId}/indexed-objects/snapshots.

        Get snapshots of indexed object.

        Args:
            protection_group_id (string): Specifies the protection group id.
            object_id (long|int): Specifies the object id.
            indexed_object_name (string): Specifies the indexed object name.
            include_indexed_snapshots_only (bool, optional): Specifies whether
                to only return snapshots which are indexed. In an indexed
                snapshots file are guaranteened to exist, while in a
                non-indexed snapshots file may not exist.
            from_time_usecs (long|int, optional): Specifies the timestamp in
                Unix time epoch in microseconds to filter indexed object's
                snapshots which are taken after this value.
            to_time_usecs (long|int, optional): Specifies the timestamp in
                Unix time epoch in microseconds to filter indexed object's
                snapshots which are taken before this value.
            run_types (list of RunType6Enum, optional): Filter by run type.
                Only protection run matching the specified types will be
                returned. By default, CDP hydration snapshots are not
                included, unless explicitly queried using this field.

        Returns:
            GetIndexedObjectSnapshotsResponseBody: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_indexed_object_snapshots called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_indexed_object_snapshots.')
            self.validate_parameters(protection_group_id=protection_group_id,
                                     object_id=object_id,
                                     indexed_object_name=indexed_object_name)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_indexed_object_snapshots.')
            _url_path = '/data-protect/objects/{objectId}/protection-groups/{protectionGroupId}/indexed-objects/snapshots'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'protectionGroupId': protection_group_id,
                'objectId': object_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'indexedObjectName': indexed_object_name,
                'includeIndexedSnapshotsOnly': include_indexed_snapshots_only,
                'fromTimeUsecs': from_time_usecs,
                'toTimeUsecs': to_time_usecs,
                'runTypes': run_types
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_indexed_object_snapshots.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_indexed_object_snapshots.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_indexed_object_snapshots')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_indexed_object_snapshots.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, GetIndexedObjectSnapshotsResponseBody.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_object_snapshot_info(self,
                                 snapshot_id):
        """Does a GET request to /data-protect/snapshots/{snapshotId}.

        Get details of object snapshot.

        Args:
            snapshot_id (string): Specifies the snapshot id.

        Returns:
            ObjectSnapshot: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_object_snapshot_info called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_object_snapshot_info.')
            self.validate_parameters(snapshot_id=snapshot_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_object_snapshot_info.')
            _url_path = '/data-protect/snapshots/{snapshotId}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'snapshotId': snapshot_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_object_snapshot_info.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_object_snapshot_info.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_object_snapshot_info')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_object_snapshot_info.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ObjectSnapshot.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_object_snapshot_volume_info(self,
                                        snapshot_id,
                                        include_supported_only=None):
        """Does a GET request to /data-protect/snapshots/{snapshotId}/volume.

        Get volume info of object snapshot.

        Args:
            snapshot_id (string): Specifies the snapshot id.
            include_supported_only (bool, optional): Specifies whether to only
                return supported volumes.

        Returns:
            CommonObjectSnapshotVolumeParams: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_object_snapshot_volume_info called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_object_snapshot_volume_info.')
            self.validate_parameters(snapshot_id=snapshot_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_object_snapshot_volume_info.')
            _url_path = '/data-protect/snapshots/{snapshotId}/volume'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'snapshotId': snapshot_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'includeSupportedOnly': include_supported_only
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_object_snapshot_volume_info.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_object_snapshot_volume_info.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_object_snapshot_volume_info')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_object_snapshot_volume_info.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CommonObjectSnapshotVolumeParams.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_source_hierarchy_objects(self,
                                     source_id,
                                     parent_id=None,
                                     tenant_ids=None,
                                     include_tenants=None,
                                     vmware_object_types=None,
                                     netapp_object_types=None,
                                     o_365_object_types=None,
                                     cassandra_object_types=None,
                                     mongodb_object_types=None,
                                     couchbase_object_types=None,
                                     hdfs_object_types=None,
                                     hbase_object_types=None,
                                     hive_object_types=None,
                                     hyperv_object_types=None,
                                     azure_object_types=None,
                                     kvm_object_types=None,
                                     aws_object_types=None,
                                     gcp_object_types=None,
                                     acropolis_object_types=None,
                                     generic_nas_object_types=None,
                                     isilon_object_types=None,
                                     flashblade_object_types=None,
                                     elastifile_object_types=None,
                                     gpfs_object_types=None,
                                     pure_object_types=None,
                                     nimble_object_types=None,
                                     physical_object_types=None,
                                     kubernetes_object_types=None,
                                     exchange_object_types=None,
                                     ad_object_types=None,
                                     mssql_object_types=None,
                                     oracle_object_types=None):
        """Does a GET request to /data-protect/sources/{sourceId}/objects.

        List objects which can be used for data protection.

        Args:
            source_id (long|int): Specifies the source ID for which objects
                should be returned.
            parent_id (long|int, optional): Specifies the parent ID under
                which objects should be returned.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Objects which belongs to all tenants which the current
                user has permission to see.
            vmware_object_types (list of VmwareObjectTypeEnum, optional):
                Specifies the VMware object types to filter objects.
            netapp_object_types (list of NetappObjectTypeEnum, optional):
                Specifies the Netapp object types to filter objects.
            o_365_object_types (list of O365ObjectTypeEnum, optional):
                Specifies the Office 365 object types to filter objects.
            cassandra_object_types (list of CassandraObjectType1Enum,
                optional): Specifies the Cassandra object types to filter
                objects.
            mongodb_object_types (list of MongodbObjectType1Enum, optional):
                Specifies the Mongo DB object types to filter objects.
            couchbase_object_types (list of CouchbaseObjectType1Enum,
                optional): Specifies the Couchbase object types to filter
                objects.
            hdfs_object_types (list of HdfsObjectTypeEnum, optional):
                Specifies the HDFS object types to filter objects.
            hbase_object_types (list of HbaseObjectType1Enum, optional):
                Specifies the Hbase object types to filter objects.
            hive_object_types (list of HiveObjectType1Enum, optional):
                Specifies the Hive object types to filter objects.
            hyperv_object_types (list of HypervObjectTypeEnum, optional):
                Specifies the HyperV object types to filter objects.
            azure_object_types (list of AzureObjectTypeEnum, optional):
                Specifies the Azure object types to filter objects.
            kvm_object_types (list of KvmObjectTypeEnum, optional): Specifies
                the KVM object types to filter objects.
            aws_object_types (list of AwsObjectTypeEnum, optional): Specifies
                the AWS object types to filter objects.
            gcp_object_types (list of GcpObjectTypeEnum, optional): Specifies
                the GCP object types to filter objects.
            acropolis_object_types (list of AcropolisObjectTypeEnum,
                optional): Specifies the Acropolis object types to filter
                objects.
            generic_nas_object_types (list of GenericNasObjectTypeEnum,
                optional): Specifies the generic NAS object types to filter
                objects.
            isilon_object_types (list of IsilonObjectTypeEnum, optional):
                Specifies the Isilon object types to filter objects.
            flashblade_object_types (list of FlashbladeObjectTypeEnum,
                optional): Specifies the Flashblade object types to filter
                objects.
            elastifile_object_types (list of ElastifileObjectTypeEnum,
                optional): Specifies the Elastifile object types to filter
                objects.
            gpfs_object_types (list of GpfsObjectTypeEnum, optional):
                Specifies the GPFS object types to filter objects.
            pure_object_types (list of PureObjectTypeEnum, optional):
                Specifies the Pure object types to filter objects.
            nimble_object_types (list of NimbleObjectTypeEnum, optional):
                Specifies the Nimble object types to filter objects.
            physical_object_types (list of PhysicalObjectTypeEnum, optional):
                Specifies the Physical object types to filter objects.
            kubernetes_object_types (list of KubernetesObjectTypeEnum,
                optional): Specifies the Kubernetes object types to filter
                objects.
            exchange_object_types (list of ExchangeObjectTypeEnum, optional):
                Specifies the Exchange object types to filter objects.
            ad_object_types (list of AdObjectTypeEnum, optional): Specifies
                the AD object types to filter objects.
            mssql_object_types (list of MssqlObjectTypeEnum, optional):
                Specifies the MSSQL object types to filter objects.
            oracle_object_types (list of OracleObjectTypeEnum, optional):
                Specifies the Oracle object types to filter objects.

        Returns:
            ObjectSummaries: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_source_hierarchy_objects called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_source_hierarchy_objects.')
            self.validate_parameters(source_id=source_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_source_hierarchy_objects.')
            _url_path = '/data-protect/sources/{sourceId}/objects'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'sourceId': source_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'parentId': parent_id,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'vmwareObjectTypes': vmware_object_types,
                'netappObjectTypes': netapp_object_types,
                'o365ObjectTypes': o_365_object_types,
                'cassandraObjectTypes': cassandra_object_types,
                'mongodbObjectTypes': mongodb_object_types,
                'couchbaseObjectTypes': couchbase_object_types,
                'hdfsObjectTypes': hdfs_object_types,
                'hbaseObjectTypes': hbase_object_types,
                'hiveObjectTypes': hive_object_types,
                'hypervObjectTypes': hyperv_object_types,
                'azureObjectTypes': azure_object_types,
                'kvmObjectTypes': kvm_object_types,
                'awsObjectTypes': aws_object_types,
                'gcpObjectTypes': gcp_object_types,
                'acropolisObjectTypes': acropolis_object_types,
                'genericNasObjectTypes': generic_nas_object_types,
                'isilonObjectTypes': isilon_object_types,
                'flashbladeObjectTypes': flashblade_object_types,
                'elastifileObjectTypes': elastifile_object_types,
                'gpfsObjectTypes': gpfs_object_types,
                'pureObjectTypes': pure_object_types,
                'nimbleObjectTypes': nimble_object_types,
                'physicalObjectTypes': physical_object_types,
                'kubernetesObjectTypes': kubernetes_object_types,
                'exchangeObjectTypes': exchange_object_types,
                'adObjectTypes': ad_object_types,
                'mssqlObjectTypes': mssql_object_types,
                'oracleObjectTypes': oracle_object_types
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_source_hierarchy_objects.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_source_hierarchy_objects.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_source_hierarchy_objects')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_source_hierarchy_objects.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ObjectSummaries.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise


    def get_snapshot_diff(self,
                          id,
                          body=None):
        """Does a PATCH request to /data-protect/objects/{id}/snapshotDiff.

        Get diff (files added/deleted) between two snapshots of a given
        object.

        Args:
            id (long|int): TODO: Type description here.
            body (SnapshotDiffParams, optional): TODO: Type description here.

        Returns:
            SnapshotDiffResult: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.
        """
        try:
            self.logger.info('get_snapshot_diff called.')

            # Validate required parameters
            self.logger.info('Validating required parameters for get_snapshot_diff.')
            self.validate_parameters(id=id)

            # Prepare query URL
            self.logger.info('Preparing query URL for get_snapshot_diff.')
            _url_path = '/data-protect/objects/{id}/snapshotDiff'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_snapshot_diff.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_snapshot_diff.')
            _request = self.http_client.patch(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_snapshot_diff')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_snapshot_diff.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SnapshotDiffResult.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
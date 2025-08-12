# -*- coding: utf-8 -*-

import logging
from cohesity_management_sdk.api_helper import APIHelper
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.base_controller import BaseController
from cohesity_management_sdk.http.auth.custom_header_auth import CustomHeaderAuth
from cohesity_management_sdk.models_v2.protection_groups import ProtectionGroups
from cohesity_management_sdk.models_v2.protection_group import ProtectionGroup
from cohesity_management_sdk.models_v2.specifies_the_response_of_updation_of_state_of_multiple_protection_groups import SpecifiesTheResponseOfUpdationOfStateOfMultipleProtectionGroups
from cohesity_management_sdk.models_v2.protection_group_runs import ProtectionGroupRuns
from cohesity_management_sdk.models_v2.update_protection_group_run_response_body import UpdateProtectionGroupRunResponseBody
from cohesity_management_sdk.models_v2.create_protection_run_response import CreateProtectionRunResponse
from cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters import CommonProtectionGroupRunResponseParameters
from cohesity_management_sdk.models_v2.perform_run_action_response import PerformRunActionResponse
from cohesity_management_sdk.models_v2.protection_runs_summary import ProtectionRunsSummary
from cohesity_management_sdk.exceptions.error_exception import ErrorException

class ProtectionGroupsController(BaseController):

    """A Controller to access Endpoints in the cohesity_management_sdk API."""

    def __init__(self, config=None, client=None, call_back=None):
        super(ProtectionGroupsController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def get_protection_groups(self,
                              ids=None,
                              names=None,
                              policy_ids=None,
                              environments=None,
                              is_active=None,
                              is_deleted=None,
                              is_paused=None,
                              last_run_local_backup_status=None,
                              last_run_replication_status=None,
                              last_run_archival_status=None,
                              last_run_cloud_spin_status=None,
                              is_last_run_sla_violated=None,
                              tenant_ids=None,
                              include_tenants=None,
                              include_last_run_info=None,
                              prune_excluded_source_ids=None):
        """Does a GET request to /data-protect/protection-groups.

        Get the list of Protection Groups.

        Args:
            ids (list of string, optional): Filter by a list of Protection
                Group ids.
            names (list of string, optional): Filter by a list of Protection
                Group names.
            policy_ids (list of string, optional): Filter by Policy ids that
                are associated with Protection Groups. Only Protection Groups
                associated with the specified Policy ids, are returned.
            environments (list of Environment21Enum, optional): Filter by
                environment types such as 'kVMware', 'kView', etc. Only
                Protection Groups protecting the specified environment types
                are returned.
            is_active (bool, optional): Filter by Inactive or Active
                Protection Groups. If not set, all Inactive and Active
                Protection Groups are returned. If true, only Active
                Protection Groups are returned. If false, only Inactive
                Protection Groups are returned. When you create a Protection
                Group on a Primary Cluster with a replication schedule, the
                Cluster creates an Inactive copy of the Protection Group on
                the Remote Cluster. In addition, when an Active and running
                Protection Group is deactivated, the Protection Group becomes
                Inactive.
            is_deleted (bool, optional): If true, return only Protection
                Groups that have been deleted but still have Snapshots
                associated with them. If false, return all Protection Groups
                except those Protection Groups that have been deleted and
                still have Snapshots associated with them. A Protection Group
                that is deleted with all its Snapshots is not returned for
                either of these cases.
            is_paused (bool, optional): Filter by paused or non paused
                Protection Groups, If not set, all paused and non paused
                Protection Groups are returned. If true, only paused
                Protection Groups are returned. If false, only non paused
                Protection Groups are returned.
            last_run_local_backup_status (list of
                LastRunLocalBackupStatusEnum, optional): Filter by last local
                backup run status.<br> 'Running' indicates that the run is
                still running.<br> 'Canceled' indicates that the run has been
                canceled.<br> 'Canceling' indicates that the run is in the
                process of being canceled.<br> 'Failed' indicates that the run
                has failed.<br> 'Missed' indicates that the run was unable to
                take place at the scheduled time because the previous run was
                still happening.<br> 'Succeeded' indicates that the run has
                finished successfully.<br> 'SucceededWithWarning' indicates
                that the run finished successfully, but there were some
                warning messages.
            last_run_replication_status (list of LastRunReplicationStatusEnum,
                optional): Filter by last remote replication run status.<br>
                'Running' indicates that the run is still running.<br>
                'Canceled' indicates that the run has been canceled.<br>
                'Canceling' indicates that the run is in the process of being
                canceled.<br> 'Failed' indicates that the run has failed.<br>
                'Missed' indicates that the run was unable to take place at
                the scheduled time because the previous run was still
                happening.<br> 'Succeeded' indicates that the run has finished
                successfully.<br> 'SucceededWithWarning' indicates that the
                run finished successfully, but there were some warning
                messages.
            last_run_archival_status (list of LastRunArchivalStatusEnum,
                optional): Filter by last cloud archival run status.<br>
                'Running' indicates that the run is still running.<br>
                'Canceled' indicates that the run has been canceled.<br>
                'Canceling' indicates that the run is in the process of being
                canceled.<br> 'Failed' indicates that the run has failed.<br>
                'Missed' indicates that the run was unable to take place at
                the scheduled time because the previous run was still
                happening.<br> 'Succeeded' indicates that the run has finished
                successfully.<br> 'SucceededWithWarning' indicates that the
                run finished successfully, but there were some warning
                messages.
            last_run_cloud_spin_status (list of LastRunCloudSpinStatusEnum,
                optional): Filter by last cloud spin run status.<br> 'Running'
                indicates that the run is still running.<br> 'Canceled'
                indicates that the run has been canceled.<br> 'Canceling'
                indicates that the run is in the process of being
                canceled.<br> 'Failed' indicates that the run has failed.<br>
                'Missed' indicates that the run was unable to take place at
                the scheduled time because the previous run was still
                happening.<br> 'Succeeded' indicates that the run has finished
                successfully.<br> 'SucceededWithWarning' indicates that the
                run finished successfully, but there were some warning
                messages.
            is_last_run_sla_violated (bool, optional): If true, return
                Protection Groups for which last run SLA was violated.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which objects are to be returned.
            include_tenants (bool, optional): If true, the response will
                include Protection Groups which were created by all tenants
                which the current user has permission to see. If false, then
                only Protection Groups created by the current user will be
                returned.
            include_last_run_info (bool, optional): If true, the response will
                include last run info. If it is false or not specified, the
                last run info won't be returned.
            prune_excluded_source_ids (bool, optional): If true, the response
                will not include the list of excluded source IDs in groups
                that contain this field. This can be set to true in order to
                improve performance if excluded source IDs are not needed by
                the user.

        Returns:
            ProtectionGroups: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_groups called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_groups.')
            _url_path = '/data-protect/protection-groups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'ids': ids,
                'names': names,
                'policyIds': policy_ids,
                'environments': environments,
                'isActive': is_active,
                'isDeleted': is_deleted,
                'isPaused': is_paused,
                'lastRunLocalBackupStatus': last_run_local_backup_status,
                'lastRunReplicationStatus': last_run_replication_status,
                'lastRunArchivalStatus': last_run_archival_status,
                'lastRunCloudSpinStatus': last_run_cloud_spin_status,
                'isLastRunSlaViolated': is_last_run_sla_violated,
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'includeLastRunInfo': include_last_run_info,
                'pruneExcludedSourceIds': prune_excluded_source_ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_protection_groups.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_groups.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_groups')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_groups.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionGroups.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_protection_group(self,
                                body):
        """Does a POST request to /data-protect/protection-groups.

        Create a Protection Group.

        Args:
            body (CreateOrUpdateProtectionGroupRequest): Specifies the
                parameters to create a Protection Group.

        Returns:
            ProtectionGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_protection_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_protection_group.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_protection_group.')
            _url_path = '/data-protect/protection-groups'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_protection_group.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_protection_group.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_protection_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_protection_group.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_protection_groups_state(self,
                                       body):
        """Does a POST request to /data-protect/protection-groups/states.

        Perform an action like pause, resume, active, deactivate on all
        specified Protection Groups. Note that the pause or resume actions
        will take effect from next Protection Run. Also, user can specify only
        one type of action on all the Protection Groups. Deactivate and
        activate actions are independent of pause and resume state. Deactivate
        and activate actions are useful in case of failover situations.
        Returns success if the state of all the Protection Groups state is
        changed successfully.

        Args:
            body (UpdateStateOfProtectionGroups): Specifies the parameters to
                perform an action of list of Protection Groups.

        Returns:
            SpecifiesTheResponseOfUpdationOfStateOfMultipleProtectionGroups:
                Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_protection_groups_state called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_protection_groups_state.')
            self.validate_parameters(body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_protection_groups_state.')
            _url_path = '/data-protect/protection-groups/states'
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_protection_groups_state.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_protection_groups_state.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_protection_groups_state')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_protection_groups_state.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, SpecifiesTheResponseOfUpdationOfStateOfMultipleProtectionGroups.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_protection_group_by_id(self,
                                   id,
                                   include_last_run_info=None,
                                   prune_excluded_source_ids=None):
        """Does a GET request to /data-protect/protection-groups/{id}.

        Returns the Protection Group corresponding to the specified Group id.

        Args:
            id (string): Specifies a unique id of the Protection Group.
            include_last_run_info (bool, optional): If true, the response will
                include last run info. If it is false or not specified, the
                last run info won't be returned.
            prune_excluded_source_ids (bool, optional): If true, the response
                will not include the list of excluded source IDs in groups
                that contain this field. This can be set to true in order to
                improve performance if excluded source IDs are not needed by
                the user.

        Returns:
            ProtectionGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_group_by_id called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_protection_group_by_id.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_group_by_id.')
            _url_path = '/data-protect/protection-groups/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'includeLastRunInfo': include_last_run_info,
                'pruneExcludedSourceIds': prune_excluded_source_ids
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_protection_group_by_id.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_group_by_id.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_group_by_id')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_group_by_id.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_protection_group(self,
                                id,
                                body):
        """Does a PUT request to /data-protect/protection-groups/{id}.

        Update the specified Protection Group.

        Args:
            id (string): Specifies the id of the Protection Group.
            body (CreateOrUpdateProtectionGroupRequest): Specifies the
                parameters to update a Protection Group.

        Returns:
            ProtectionGroup: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_protection_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_protection_group.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_protection_group.')
            _url_path = '/data-protect/protection-groups/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_protection_group.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_protection_group.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_protection_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_protection_group.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionGroup.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_protection_group(self,
                                id,
                                delete_snapshots=None,
                                reason=None):
        """Does a DELETE request to /data-protect/protection-groups/{id}.

        Returns Success if the Protection Group is deleted.

        Args:
            id (string): Specifies a unique id of the Protection Group.
            delete_snapshots (bool, optional): Specifies if Snapshots
                generated by the Protection Group should also be deleted when
                the Protection Group is deleted.
            reason (string): Specifies the reason for group deletion with or without snapshots

        Returns:
            void: Response from the API. No Content

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_protection_group called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for delete_protection_group.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_protection_group.')
            _url_path = '/data-protect/protection-groups/{id}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'deleteSnapshots': delete_snapshots,
                'reason': reason
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for delete_protection_group.')
            _headers = {
                'accept'       : 'application/json' ,
                'content-type' : 'application/json; charset=utf-8'
            }

            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_protection_group.')
            _request = self.http_client.delete(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'delete_protection_group')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_protection_group.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_protection_group_runs(self,
                                  id,
                                  run_id=None,
                                  start_time_usecs=None,
                                  end_time_usecs=None,
                                  tenant_ids=None,
                                  include_tenants=None,
                                  run_types=None,
                                  include_object_details=None,
                                  local_backup_run_status=None,
                                  replication_run_status=None,
                                  archival_run_status=None,
                                  cloud_spin_run_status=None,
                                  num_runs=None,
                                  exclude_non_restorable_runs=False,
                                  run_tags=None,
                                  only_return_shell_info=None,
                                  exclude_error_runs=None,
                                  job_run_start_time_usecs=None,
                                  only_return_data_migration_jobs=None,
                                  include_extension_info=None,
                                  include_rpo_snapshots=None,
                                  source_id=None):
        """Does a GET request to /data-protect/protection-groups/{id}/runs.

        Get the runs for a particular Protection Group.

        Args:
            id (string): Specifies a unique id of the Protection Group.
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
            include_object_details (bool, optional): Specifies if the result
                includes the object details for each protection run. If set to
                true, details of the protected object will be returned. If set
                to false or not specified, details will not be returned.
            local_backup_run_status (list of LocalBackupRunStatusEnum,
                optional): Specifies a list of local backup status, runs
                matching the status will be returned.<br> 'Running' indicates
                that the run is still running.<br> 'Canceled' indicates that
                the run has been canceled.<br> 'Canceling' indicates that the
                run is in the process of being canceled.<br> 'Failed'
                indicates that the run has failed.<br> 'Missed' indicates that
                the run was unable to take place at the scheduled time because
                the previous run was still happening.<br> 'Succeeded'
                indicates that the run has finished successfully.<br>
                'SucceededWithWarning' indicates that the run finished
                successfully, but there were some warning messages.
            replication_run_status (list of ReplicationRunStatusEnum,
                optional): Specifies a list of replication status, runs
                matching the status will be returned.<br> 'Running' indicates
                that the run is still running.<br> 'Canceled' indicates that
                the run has been canceled.<br> 'Canceling' indicates that the
                run is in the process of being canceled.<br> 'Failed'
                indicates that the run has failed.<br> 'Missed' indicates that
                the run was unable to take place at the scheduled time because
                the previous run was still happening.<br> 'Succeeded'
                indicates that the run has finished successfully.<br>
                'SucceededWithWarning' indicates that the run finished
                successfully, but there were some warning messages.
            archival_run_status (list of ArchivalRunStatusEnum, optional):
                Specifies a list of archival status, runs matching the status
                will be returned.<br> 'Running' indicates that the run is
                still running.<br> 'Canceled' indicates that the run has been
                canceled.<br> 'Canceling' indicates that the run is in the
                process of being canceled.<br> 'Failed' indicates that the run
                has failed.<br> 'Missed' indicates that the run was unable to
                take place at the scheduled time because the previous run was
                still happening.<br> 'Succeeded' indicates that the run has
                finished successfully.<br> 'SucceededWithWarning' indicates
                that the run finished successfully, but there were some
                warning messages.
            cloud_spin_run_status (list of CloudSpinRunStatusEnum, optional):
                Specifies a list of cloud spin status, runs matching the
                status will be returned.<br> 'Running' indicates that the run
                is still running.<br> 'Canceled' indicates that the run has
                been canceled.<br> 'Canceling' indicates that the run is in
                the process of being canceled.<br> 'Failed' indicates that the
                run has failed.<br> 'Missed' indicates that the run was unable
                to take place at the scheduled time because the previous run
                was still happening.<br> 'Succeeded' indicates that the run
                has finished successfully.<br> 'SucceededWithWarning'
                indicates that the run finished successfully, but there were
                some warning messages.
            num_runs (long|int, optional): Specifies the max number of runs.
                If not specified, at most 100 runs will be returned.
            exclude_non_restorable_runs (bool, optional): Specifies whether to
                exclude non restorable runs. Run is treated restorable only if
                there is atleast one object snapshot (which may be either a
                local or an archival snapshot) which is not deleted or
                expired. Default value is false.
            run_tags (list of string): Specifies a list of tags for protection
                runs. If this is specified, only the runs which match these
                tags will be returned.
            only_return_shell_info (bool, optional): If set, returns only shell info such as run's start time, type,
                error if any.
            exclude_error_runs (bool, optional): Specifies whether to exclude runs with error. If no value is
               specified, then runs with errors are included.
            job_run_start_time_usecs (long|int, optional): Return a specific Job Run by specifying a time and a group id.
               Specify the time when the Job Run started as a Unix epoch Timestamp (in
               microseconds). If this field is specified, jobId must also be specified.
            only_return_data_migration_jobs (bool, optional): If set, returns only shell info such as run's start time, type,
               error if any.
            include_extension_info (bool, optional): Specifies if needs to include proto extensions if they are extended.
            include_rpo_snapshots (bool, optional): If true, then the snapshots for Protection Sources protected
               by Rpo policies will also be returned.
            source_id (long|int, optional):  Filter by source id. Only Job Runs protecting the specified source
               (such as a VM or View) are returned. The source id is assigned by the Cohesity
               Cluster.

        Returns:
            ProtectionGroupRuns: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_group_runs called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_protection_group_runs.')
            self.validate_parameters(id=id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_group_runs.')
            _url_path = '/data-protect/protection-groups/{id}/runs'
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
                'includeObjectDetails': include_object_details,
                'localBackupRunStatus': local_backup_run_status,
                'replicationRunStatus': replication_run_status,
                'archivalRunStatus': archival_run_status,
                'cloudSpinRunStatus': cloud_spin_run_status,
                'numRuns': num_runs,
                'excludeNonRestorableRuns': exclude_non_restorable_runs,
                "runTags": run_tags,
                "onlyReturnShellInfo": only_return_shell_info,
                "excludeErrorRuns": exclude_error_runs,
                "jobRunStartTimeUsecs": job_run_start_time_usecs,
                "onlyReturnDataMigrationJobs": only_return_data_migration_jobs,
                "includeExtensionInfo": include_extension_info,
                "includeRpoSnapshots": include_rpo_snapshots,
                "sourceId": source_id
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_protection_group_runs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_group_runs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_group_runs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_group_runs.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionGroupRuns.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_protection_group_run(self,
                                    id,
                                    body):
        """Does a PUT request to /data-protect/protection-groups/{id}/runs.

        Update runs for a particular Protection Group. A user can perform the
        following actions: 1. Extend or reduce retention of a local,
        replication and archival snapshots. 2. Can perform resync operation on
        failed copy snapshots attempts in this Run. 3. Add new replication and
        archival snapshot targets to the Run. 4. Add or remove legal hold on
        the snapshots. Only a user with DSO role can perform this operation.
        5. Delete the snapshots that were created as a part of this Run. 6.
        Apply datalock on existing snapshots where a user cannot manually
        delete snapshots before the expiry time. 

        Args:
            id (string): Specifies a unique id of the Protection Group.
            body (UpdateProtectionGroupRunRequestBody): Specifies the
                parameters to update a Protection Group Run.

        Returns:
            UpdateProtectionGroupRunResponseBody: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_protection_group_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for update_protection_group_run.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_protection_group_run.')
            _url_path = '/data-protect/protection-groups/{id}/runs'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_protection_group_run.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_protection_group_run.')
            _request = self.http_client.put(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'update_protection_group_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_protection_group_run.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, UpdateProtectionGroupRunResponseBody.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def create_protection_group_run(self,
                                    id,
                                    body):
        """Does a POST request to /data-protect/protection-groups/{id}/runs.

        Create a new protection run. This can be used to start a run for a
        Protection Group on demand, ignoring the schedule and retention
        specified in the protection policy.

        Args:
            id (string): Specifies a unique id of the Protection Group.
            body (CreateProtectionGroupRunRequest): Specifies the parameters
                to start a protection run.

        Returns:
            CreateProtectionRunResponse: Response from the API. Accepted

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_protection_group_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for create_protection_group_run.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_protection_group_run.')
            _url_path = '/data-protect/protection-groups/{id}/runs'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_protection_group_run.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_protection_group_run.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'create_protection_group_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_protection_group_run.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CreateProtectionRunResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_protection_group_run(self,
                                 id,
                                 run_id,
                                 tenant_ids=None,
                                 include_tenants=None,
                                 include_object_details=None):
        """Does a GET request to /data-protect/protection-groups/{id}/runs/{runId}.

        Get a run for a particular Protection Group.

        Args:
            id (string): Specifies a unique id of the Protection Group.
            run_id (string): Specifies a unique run id of the Protection Group
                run.
            tenant_ids (list of string, optional): TenantIds contains ids of
                the tenants for which the run is to be returned.
            include_tenants (bool, optional): If true, the response will
                include Protection Group Runs which were created by all
                tenants which the current user has permission to see. If
                false, then only Protection Groups created by the current user
                will be returned. If it's not specified, it is true by
                default.
            include_object_details (bool, optional): Specifies if the result
                includes the object details for a protection run. If set to
                true, details of the protected object will be returned. If set
                to false or not specified, details will not be returned.

        Returns:
            CommonProtectionGroupRunResponseParameters: Response from the API.
                Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_group_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_protection_group_run.')
            self.validate_parameters(id=id,
                                     run_id=run_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_group_run.')
            _url_path = '/data-protect/protection-groups/{id}/runs/{runId}'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id,
                'runId': run_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'tenantIds': tenant_ids,
                'includeTenants': include_tenants,
                'includeObjectDetails': include_object_details
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for get_protection_group_run.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_group_run.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_group_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_group_run.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, CommonProtectionGroupRunResponseParameters.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def perform_action_on_protection_group_run(self, id, body):
        """Does a POST request to /data-protect/protection-groups/{id}/runs/actions.

        Perform various actions on a Protection Group run.

        Args:
            id (string): Specifies a unique id of the Protection Group.
            body (PerformActionOnProtectionGroupRunRequest): Specifies the
                parameters to perform an action on a protection run.

        Returns:
            PerformRunActionResponse: Response from the API. Accepted

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('perform_action_on_protection_group_run called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for perform_action_on_protection_group_run.')
            self.validate_parameters(id=id,
                                     body=body)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for perform_action_on_protection_group_run.')
            _url_path = '/data-protect/protection-groups/{id}/runs/actions'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id,
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for perform_action_on_protection_group_run.')
            _headers = {
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for perform_action_on_protection_group_run.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'perform_action_on_protection_group_run')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for perform_action_on_protection_group_run.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

            # Return appropriate type
            return APIHelper.json_deserialize(
                _context.response.raw_body, PerformRunActionResponse.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_run_errors_report(self,
                              id,
                              run_id,
                              object_id):
        """Does a GET request to /data-protect/protection-groups/{id}/runs/{runId}/objects/{objectId}/downloadMessages.

        Get an CSV error report for given objectId and run id. Each row in CSV
        report contains the File Path, error/warning code and error/warning
        message.

        Args:
            id (string): Specifies a unique id of the Protection Group.
            run_id (string): Specifies a unique run id of the Protection Group
                run.
            object_id (string): Specifies the id of the object for which
                errors/warnings are to be returned.

        Returns:
            void: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_run_errors_report called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_run_errors_report.')
            self.validate_parameters(id=id,
                                     run_id=run_id,
                                     object_id=object_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_run_errors_report.')
            _url_path = '/data-protect/protection-groups/{id}/runs/{runId}/objects/{objectId}/downloadMessages'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id,
                'runId': run_id,
                'objectId': object_id
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_url = APIHelper.clean_url(_query_builder)

            # Prepare headers
            self.logger.info('Preparing headers for get_run_errors_report.')
            _headers = { 'accept' : 'application/json' }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_run_errors_report.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_run_errors_report')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_run_errors_report.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def get_protection_runs(self,
                            start_time_usecs=None,
                            end_time_usecs=None,
                            run_status=None):
        """Does a GET request to /data-protect/runs/summary.

        Get a list of protection runs.

        Args:
            start_time_usecs (long|int, optional): Filter by a start time.
                Specify the start time as a Unix epoch Timestamp (in
                microseconds), only runs executing after this time will be
                returned. By default it is endTimeUsecs minus an hour.
            end_time_usecs (long|int, optional): Filter by a end time. Specify
                the start time as a Unix epoch Timestamp (in microseconds),
                only runs executing before this time will be returned. By
                default it is current time.
            run_status (list of RunStatusEnum, optional): Specifies a list of
                status, runs matching the status will be returned.<br>
                'Running' indicates that the run is still running.<br>
                'Canceled' indicates that the run has been canceled.<br>
                'Canceling' indicates that the run is in the process of being
                canceled.<br> 'Failed' indicates that the run has failed.<br>
                'Missed' indicates that the run was unable to take place at
                the scheduled time because the previous run was still
                happening.<br> 'Succeeded' indicates that the run has finished
                successfully.<br> 'SucceededWithWarning' indicates that the
                run finished successfully, but there were some warning
                messages.

        Returns:
            ProtectionRunsSummary: Response from the API. Success

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_protection_runs called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_protection_runs.')
            _url_path = '/data-protect/runs/summary'
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
            self.logger.info('Preparing headers for get_protection_runs.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_runs.')
            _request = self.http_client.get(_query_url, headers=_headers)
            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_runs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_protection_runs.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body, ProtectionRunsSummary.from_dictionary)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise


    def get_runs_report(self, id, run_id, object_id, file_type=None):
        """Does a GET request to /data-protect/protection-groups/{id}/runs/{runId}/objects/{objectId}/downloadFiles.

        Get an CSV report for given objectId and run id. Report will depend
        on the query parameter fileType, default will be: success_files_list
        where each row contains the name of file backedup successfully.

        Args:
            id (string): Specifies a unique id of the Protection Group.
            run_id (string): Specifies a unique run id of the Protection
                Group run.
            object_id (String): Specifies the id of the object for which
                errors/warnings are to be returned.
            file_type (string): Specifies the downloaded type, i.e:
                success_files_list, default: success_files_list

        Returns:
            void: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('get_runs_report called.')
    
            # Validate required parameters
            self.logger.info('Validating required parameters for get_runs_report.')
            self.validate_parameters(id=id, run_id=run_id, object_id=object_id)
    
            # Prepare query URL
            self.logger.info('Preparing query URL for get_runs_report.')
            _url_path = '/data-protect/protection-groups/{id}/runs/{runId}/objects/{objectId}/downloadFiles'
            _url_path = APIHelper.append_url_with_template_parameters(_url_path, { 
                'id': id,
                'runId': run_id,
                'objectId': object_id                
            })
            _query_builder = self.config.get_base_uri()
            _query_builder += _url_path
            _query_parameters = {
                'fileType': file_type
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, ConfigurationV2.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
            _headers = {
                'content-type': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for get_protection_runs.')
            _request = self.http_client.get(_query_url, headers=_headers)

            CustomHeaderAuth.apply(_request, self.config)
            _context = self.execute_request(_request, name = 'get_protection_runs')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for get_runs_report.')
            if _context.response.status_code == 0:
                raise ErrorException('Error', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_of_day
import cohesity_management_sdk.models_v2.sla_rule
import cohesity_management_sdk.models_v2.vmware_object_protection_update_request_params
import cohesity_management_sdk.models_v2.common_nas_protection_params
import cohesity_management_sdk.models_v2.gpfs_object_protection_update_request_params
import cohesity_management_sdk.models_v2.elastifile_object_protection_update_request_params
import cohesity_management_sdk.models_v2.netapp_object_protection_update_request_params
import cohesity_management_sdk.models_v2.isilon_object_protection_update_request_params
import cohesity_management_sdk.models_v2.flashblade_object_protection_update_request_params
import cohesity_management_sdk.models_v2.common_mssql_object_protection_params
import cohesity_management_sdk.models_v2.office_365_object_protection_common_params

class UpdateProtectedObjectsRequest(object):

    """Implementation of the 'UpdateProtectedObjectsRequest' model.

    Specifies the request to update an object backup configuration.

    Attributes:
        policy_id (string): Specifies the unique id of the Protection Policy.
            The Policy settings will be attached with every object and will be
            used in backup.
        storage_domain_id (long|int): Specifies the Storage Domain (View Box)
            ID where the object backup will be taken. This is not required if
            Cloud archive direct is benig used.
        start_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.
        priority (PriorityEnum): Specifies the priority for the objects
            backup.
        sla (list of SlaRule): Specifies the SLA parameters for list of
            objects.
        qos_policy (QosPolicyEnum): Specifies whether object backup will be
            written to HDD or SSD.
        abort_in_blackouts (bool): Specifies whether currently executing
            object backup should abort if a blackout period specified by a
            policy starts. Available only if the selected policy has at least
            one blackout period. Default value is false.
        environment (Environment15Enum): Specifies the environment for current
            object.
        vmware_params (VmwareObjectProtectionUpdateRequestParams): Specifies
            the parameters which are specific to VMware object protection.
        generic_nas_params (CommonNasProtectionParams): Specifies the update
            parameters which are specific to Generic NAS object protection.
        gpfs_params (GpfsObjectProtectionUpdateRequestParams): Specifies the
            update parameters which are specific to Gpfs object protection.
        elastifile_params (ElastifileObjectProtectionUpdateRequestParams):
            Specifies the update parameters which are specific to Elastifile
            object protection.
        netapp_params (NetappObjectProtectionUpdateRequestParams): Specifies
            the update parameters which are specific to Netapp object
            protection.
        isilon_params (IsilonObjectProtectionUpdateRequestParams): Specifies
            the update parameters which are specific to Isilon object
            protection.
        flashblade_params (FlashbladeObjectProtectionUpdateRequestParams):
            Specifies the update parameters which are specific to Flashblade
            object protection.
        mssql_params (CommonMssqlObjectProtectionParams): Specifies the update
            parameters specific to MSSQL object protection.
        office_365_user_mailbox_params
            (Office365ObjectProtectionCommonParams): Specifies the update
            parameters specific to Microsoft 365 User Mailbox object
            protection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "policy_id":'policyId',
        "storage_domain_id":'storageDomainId',
        "start_time":'startTime',
        "priority":'priority',
        "sla":'sla',
        "qos_policy":'qosPolicy',
        "abort_in_blackouts":'abortInBlackouts',
        "environment":'environment',
        "vmware_params":'vmwareParams',
        "generic_nas_params":'genericNasParams',
        "gpfs_params":'gpfsParams',
        "elastifile_params":'elastifileParams',
        "netapp_params":'netappParams',
        "isilon_params":'isilonParams',
        "flashblade_params":'flashbladeParams',
        "mssql_params":'mssqlParams',
        "office_365_user_mailbox_params":'office365UserMailboxParams'
    }

    def __init__(self,
                 policy_id=None,
                 storage_domain_id=None,
                 start_time=None,
                 priority=None,
                 sla=None,
                 qos_policy=None,
                 abort_in_blackouts=None,
                 environment=None,
                 vmware_params=None,
                 generic_nas_params=None,
                 gpfs_params=None,
                 elastifile_params=None,
                 netapp_params=None,
                 isilon_params=None,
                 flashblade_params=None,
                 mssql_params=None,
                 office_365_user_mailbox_params=None):
        """Constructor for the UpdateProtectedObjectsRequest class"""

        # Initialize members of the class
        self.policy_id = policy_id
        self.storage_domain_id = storage_domain_id
        self.start_time = start_time
        self.priority = priority
        self.sla = sla
        self.qos_policy = qos_policy
        self.abort_in_blackouts = abort_in_blackouts
        self.environment = environment
        self.vmware_params = vmware_params
        self.generic_nas_params = generic_nas_params
        self.gpfs_params = gpfs_params
        self.elastifile_params = elastifile_params
        self.netapp_params = netapp_params
        self.isilon_params = isilon_params
        self.flashblade_params = flashblade_params
        self.mssql_params = mssql_params
        self.office_365_user_mailbox_params = office_365_user_mailbox_params


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        policy_id = dictionary.get('policyId')
        storage_domain_id = dictionary.get('storageDomainId')
        start_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None
        priority = dictionary.get('priority')
        sla = None
        if dictionary.get("sla") is not None:
            sla = list()
            for structure in dictionary.get('sla'):
                sla.append(cohesity_management_sdk.models_v2.sla_rule.SlaRule.from_dictionary(structure))
        qos_policy = dictionary.get('qosPolicy')
        abort_in_blackouts = dictionary.get('abortInBlackouts')
        environment = dictionary.get('environment')
        vmware_params = cohesity_management_sdk.models_v2.vmware_object_protection_update_request_params.VmwareObjectProtectionUpdateRequestParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None
        generic_nas_params = cohesity_management_sdk.models_v2.common_nas_protection_params.CommonNasProtectionParams.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        gpfs_params = cohesity_management_sdk.models_v2.gpfs_object_protection_update_request_params.GpfsObjectProtectionUpdateRequestParams.from_dictionary(dictionary.get('gpfsParams')) if dictionary.get('gpfsParams') else None
        elastifile_params = cohesity_management_sdk.models_v2.elastifile_object_protection_update_request_params.ElastifileObjectProtectionUpdateRequestParams.from_dictionary(dictionary.get('elastifileParams')) if dictionary.get('elastifileParams') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_object_protection_update_request_params.NetappObjectProtectionUpdateRequestParams.from_dictionary(dictionary.get('netappParams')) if dictionary.get('netappParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_object_protection_update_request_params.IsilonObjectProtectionUpdateRequestParams.from_dictionary(dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        flashblade_params = cohesity_management_sdk.models_v2.flashblade_object_protection_update_request_params.FlashbladeObjectProtectionUpdateRequestParams.from_dictionary(dictionary.get('flashbladeParams')) if dictionary.get('flashbladeParams') else None
        mssql_params = cohesity_management_sdk.models_v2.common_mssql_object_protection_params.CommonMssqlObjectProtectionParams.from_dictionary(dictionary.get('mssqlParams')) if dictionary.get('mssqlParams') else None
        office_365_user_mailbox_params = cohesity_management_sdk.models_v2.office_365_object_protection_common_params.Office365ObjectProtectionCommonParams.from_dictionary(dictionary.get('office365UserMailboxParams')) if dictionary.get('office365UserMailboxParams') else None

        # Return an object of this model
        return cls(policy_id,
                   storage_domain_id,
                   start_time,
                   priority,
                   sla,
                   qos_policy,
                   abort_in_blackouts,
                   environment,
                   vmware_params,
                   generic_nas_params,
                   gpfs_params,
                   elastifile_params,
                   netapp_params,
                   isilon_params,
                   flashblade_params,
                   mssql_params,
                   office_365_user_mailbox_params)



# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.environment_type_job_params
import cohesity_management_sdk.models_v2.protection_group_alerting_policy

class RPOPolicySettings(object):

    """Implementation of the 'RPOPolicySettings' model.

    Specifies all the additional settings that are applicable only to
      an RPO policy. This can include storage domain, settings of different environments,
      etc.

    Attributes:
        alerting_policy (ProtectionGroupAlertingPolicy): Specifies the alerting policy
        backup_qos_principal (BackupQosPrincipalEnum): Specifies whether the data will be written to HDD or SSD.
        env_backup_params (EnvironmentTypeJobParams): Specifies the policy level additional environment specific backup
          params. If this is not specified, default actions will be taken,  for example
          for NAS environments, all objects within the source will be backed up.
        indexing_policy (IndexingPolicy): Specifies settings for indexing files found in an Object so these
          files can be searched and recovered. This also specifies inclusion and exclusion
          rules that determine the directories to index.
        storage_domain_id (long|int): Specifies settings for indexing files found in an Object so these
          files can be searched and recovered. This also specifies inclusion and exclusion
          rules that determine the directories to index.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "alerting_policy":'alertingPolicy',
        "backup_qos_principal":'backupQosPrincipal',
        "env_backup_params":'envBackupParams',
        "indexing_policy":'indexingPolicy',
        "storage_domain_id":'storageDomainId'
    }

    def __init__(self,
                 alerting_policy=None,
                 backup_qos_principal=None,
                 env_backup_params=None,
                 indexing_policy=None,
                 storage_domain_id=None):
        """Constructor for the RPOPolicySettings class"""

        # Initialize members of the class
        self.alerting_policy = alerting_policy
        self.backup_qos_principal = backup_qos_principal
        self.env_backup_params = env_backup_params
        self.indexing_policy = indexing_policy
        self.storage_domain_id = storage_domain_id


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
        alerting_policy = cohesity_management_sdk.models_v2.protection_group_alerting_policy.ProtectionGroupAlertingPolicy.from_dictionary(
            dictionary.get('alertingPolicy')) if dictionary.get('alertingPolicy') else None
        backup_qos_principal = dictionary.get('backupQosPrincipal')
        env_backup_params = cohesity_management_sdk.models_v2.environment_type_job_params.EnvironmentTypeJobParams.from_dictionary(
            dictionary.get('envBackupParams')) if dictionary.get('envBackupParams') else None
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        storage_domain_id = dictionary.get('storageDomainId')

        # Return an object of this model
        return cls(alerting_policy,
                   backup_qos_principal,
                   env_backup_params,
                   indexing_policy,
                   storage_domain_id)
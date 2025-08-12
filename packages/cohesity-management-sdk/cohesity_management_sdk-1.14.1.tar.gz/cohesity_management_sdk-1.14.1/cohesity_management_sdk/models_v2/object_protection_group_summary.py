# -*- coding: utf-8 -*-


class ObjectProtectionGroupSummary(object):

    """Implementation of the 'ObjectProtectionGroupSummary' model.

    Specifies a summary of a protection group protecting this object.

    Attributes:
        name (string): Specifies the protection group name.
        id (string): Specifies the protection group id.
        policy_name (string): Specifies the policy name for this group.
        policy_id (string): Specifies the policy id for this group.
        last_backup_run_status (LastBackupRunStatusEnum): Specifies the status
            of last local back up run.
        last_archival_run_status (LastArchivalRunStatusEnum): Specifies the
            status of last archival run.
        last_replication_run_status (LastReplicationRunStatusEnum): Specifies
            the status of last replication run.
        last_run_sla_violated (bool): Specifies if the sla is violated in last
            run.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "id":'id',
        "policy_name":'policyName',
        "policy_id":'policyId',
        "last_backup_run_status":'lastBackupRunStatus',
        "last_archival_run_status":'lastArchivalRunStatus',
        "last_replication_run_status":'lastReplicationRunStatus',
        "last_run_sla_violated":'lastRunSlaViolated'
    }

    def __init__(self,
                 name=None,
                 id=None,
                 policy_name=None,
                 policy_id=None,
                 last_backup_run_status=None,
                 last_archival_run_status=None,
                 last_replication_run_status=None,
                 last_run_sla_violated=None):
        """Constructor for the ObjectProtectionGroupSummary class"""

        # Initialize members of the class
        self.name = name
        self.id = id
        self.policy_name = policy_name
        self.policy_id = policy_id
        self.last_backup_run_status = last_backup_run_status
        self.last_archival_run_status = last_archival_run_status
        self.last_replication_run_status = last_replication_run_status
        self.last_run_sla_violated = last_run_sla_violated


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
        name = dictionary.get('name')
        id = dictionary.get('id')
        policy_name = dictionary.get('policyName')
        policy_id = dictionary.get('policyId')
        last_backup_run_status = dictionary.get('lastBackupRunStatus')
        last_archival_run_status = dictionary.get('lastArchivalRunStatus')
        last_replication_run_status = dictionary.get('lastReplicationRunStatus')
        last_run_sla_violated = dictionary.get('lastRunSlaViolated')

        # Return an object of this model
        return cls(name,
                   id,
                   policy_name,
                   policy_id,
                   last_backup_run_status,
                   last_archival_run_status,
                   last_replication_run_status,
                   last_run_sla_violated)



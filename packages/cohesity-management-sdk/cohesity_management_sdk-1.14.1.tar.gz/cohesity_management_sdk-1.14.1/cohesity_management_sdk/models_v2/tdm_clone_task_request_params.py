# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_clone_task

class TdmCloneTaskRequestParams(object):

    """Implementation of the 'TdmCloneTaskRequestParams' model.

    Specifies the request parameters to create a clone task.

    Attributes:
        environment (Environment10Enum): Specifies the environment of the TDM
            Clone task.
        protection_group_id (string): Specifies the ID of an existing
            protection group, which should start protecting this clone.
            Specifying this implies that the clone is eligible for automated
            snapshots based on the policy configuration. If this is specified,
            policyId should also be specified and protectionGroupName should
            not be specified.
        protection_group_name (string): Specifies the name of a new protection
            group, which should be created to protect this clone. Specifying
            this implies that the clone is eligible for automated snapshots
            based on the policy configuration. If this is specified, policyId
            should also be specified and protectionGroupId should not be
            specified.
        policy_id (string): Specifies the ID of the policy, which should be
            used to protect this clone. This is useful for automatic
            snapshots. This must be specified if either of protectionGroupId
            and protectionGroupName is specified.
        snapshot_id (string): Specifies the snapshot ID, from which the clone
            is to be created.
        target_host_id (string): Specifies the ID of the host, where the clone
            needs to be created.
        point_in_time_usecs (long|int): Specifies the timestamp (in usecs from
            epoch) for creating the clone at a point in time in the past.
        oracle_params (OracleCloneTask): Specifies the information about an
            Oracle clone task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "snapshot_id":'snapshotId',
        "target_host_id":'targetHostId',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "policy_id":'policyId',
        "point_in_time_usecs":'pointInTimeUsecs',
        "oracle_params":'oracleParams'
    }

    def __init__(self,
                 environment=None,
                 snapshot_id=None,
                 target_host_id=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 policy_id=None,
                 point_in_time_usecs=None,
                 oracle_params=None):
        """Constructor for the TdmCloneTaskRequestParams class"""

        # Initialize members of the class
        self.environment = environment
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.policy_id = policy_id
        self.snapshot_id = snapshot_id
        self.target_host_id = target_host_id
        self.point_in_time_usecs = point_in_time_usecs
        self.oracle_params = oracle_params


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
        environment = dictionary.get('environment')
        snapshot_id = dictionary.get('snapshotId')
        target_host_id = dictionary.get('targetHostId')
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        policy_id = dictionary.get('policyId')
        point_in_time_usecs = dictionary.get('pointInTimeUsecs')
        oracle_params = cohesity_management_sdk.models_v2.oracle_clone_task.OracleCloneTask.from_dictionary(dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None

        # Return an object of this model
        return cls(environment,
                   snapshot_id,
                   target_host_id,
                   protection_group_id,
                   protection_group_name,
                   policy_id,
                   point_in_time_usecs,
                   oracle_params)



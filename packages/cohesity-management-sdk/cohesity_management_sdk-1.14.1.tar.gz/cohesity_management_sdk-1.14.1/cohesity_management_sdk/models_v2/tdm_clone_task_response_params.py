# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_snapshot
import cohesity_management_sdk.models_v2.object_summary
import cohesity_management_sdk.models_v2.view
import cohesity_management_sdk.models_v2.oracle_clone_task

class TdmCloneTaskResponseParams(object):

    """Implementation of the 'TdmCloneTaskResponseParams' model.

    Specifies the response parameters for a clone task.

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
        snapshot (ObjectSnapshot): Specifies the details of the snapshot used
            for cloning.
        parent (ObjectSummary): Specifies the details of the parent object of
            the clone.
        target (ObjectSummary): Specifies the details of the target, where the
            clone is created.
        view (View): Specifies the details of the view, which is used for the
            clone.
        oracle_params (OracleCloneTask): Specifies the information about an
            Oracle clone task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "policy_id":'policyId',
        "snapshot":'snapshot',
        "parent":'parent',
        "target":'target',
        "view":'view',
        "oracle_params":'oracleParams'
    }

    def __init__(self,
                 environment=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 policy_id=None,
                 snapshot=None,
                 parent=None,
                 target=None,
                 view=None,
                 oracle_params=None):
        """Constructor for the TdmCloneTaskResponseParams class"""

        # Initialize members of the class
        self.environment = environment
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.policy_id = policy_id
        self.snapshot = snapshot
        self.parent = parent
        self.target = target
        self.view = view
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
        protection_group_id = dictionary.get('protectionGroupId')
        protection_group_name = dictionary.get('protectionGroupName')
        policy_id = dictionary.get('policyId')
        snapshot = cohesity_management_sdk.models_v2.object_snapshot.ObjectSnapshot.from_dictionary(dictionary.get('snapshot')) if dictionary.get('snapshot') else None
        parent = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('parent')) if dictionary.get('parent') else None
        target = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('target')) if dictionary.get('target') else None
        view = cohesity_management_sdk.models_v2.view.View.from_dictionary(dictionary.get('view')) if dictionary.get('view') else None
        oracle_params = cohesity_management_sdk.models_v2.oracle_clone_task.OracleCloneTask.from_dictionary(dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None

        # Return an object of this model
        return cls(environment,
                   protection_group_id,
                   protection_group_name,
                   policy_id,
                   snapshot,
                   parent,
                   target,
                   view,
                   oracle_params)



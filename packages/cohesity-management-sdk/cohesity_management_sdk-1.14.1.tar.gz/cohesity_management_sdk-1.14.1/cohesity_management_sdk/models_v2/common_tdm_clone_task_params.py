# -*- coding: utf-8 -*-


class CommonTdmCloneTaskParams(object):

    """Implementation of the 'CommonTdmCloneTaskParams' model.

    Specifies the common params for a TDM clone task.

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

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "protection_group_id":'protectionGroupId',
        "protection_group_name":'protectionGroupName',
        "policy_id":'policyId'
    }

    def __init__(self,
                 environment=None,
                 protection_group_id=None,
                 protection_group_name=None,
                 policy_id=None):
        """Constructor for the CommonTdmCloneTaskParams class"""

        # Initialize members of the class
        self.environment = environment
        self.protection_group_id = protection_group_id
        self.protection_group_name = protection_group_name
        self.policy_id = policy_id


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

        # Return an object of this model
        return cls(environment,
                   protection_group_id,
                   protection_group_name,
                   policy_id)



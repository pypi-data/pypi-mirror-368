# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_protection_group_run_params
import cohesity_management_sdk.models_v2.aws_target_params_3

class RecoverAWSAuroraParams1(object):

    """Implementation of the 'Recover AWS Aurora params.1' model.

    Specifies the parameters to recover AWS Aurora.

    Attributes:
        recover_protection_group_runs_params (list of
            RecoverProtectionGroupRunParams): Specifies the Protection Group
            Runs params to recover. All the Aurora instances that are
            successfully backed up by specified Runs will be recovered. This
            can be specified along with individual snapshots of Aurora
            instances. User has to make sure specified Object snapshots and
            Protection Group Runs should not have any intersection. For
            example, user cannot specify multiple Runs which has same Object
            or an Object snapshot and a Run which has same Object's snapshot.
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        aws_target_params (AwsTargetParams3): Specifies the params for
            recovering to an AWS target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "recover_protection_group_runs_params":'recoverProtectionGroupRunsParams',
        "aws_target_params":'awsTargetParams'
    }

    def __init__(self,
                 target_environment='kAWS',
                 recover_protection_group_runs_params=None,
                 aws_target_params=None):
        """Constructor for the RecoverAWSAuroraParams1 class"""

        # Initialize members of the class
        self.recover_protection_group_runs_params = recover_protection_group_runs_params
        self.target_environment = target_environment
        self.aws_target_params = aws_target_params


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
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kAWS'
        recover_protection_group_runs_params = None
        if dictionary.get("recoverProtectionGroupRunsParams") is not None:
            recover_protection_group_runs_params = list()
            for structure in dictionary.get('recoverProtectionGroupRunsParams'):
                recover_protection_group_runs_params.append(cohesity_management_sdk.models_v2.recover_protection_group_run_params.RecoverProtectionGroupRunParams.from_dictionary(structure))
        aws_target_params = cohesity_management_sdk.models_v2.aws_target_params_3.AwsTargetParams3.from_dictionary(dictionary.get('awsTargetParams')) if dictionary.get('awsTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   recover_protection_group_runs_params,
                   aws_target_params)



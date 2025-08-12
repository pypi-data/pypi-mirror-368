# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_s_3_bucket_restore_filter_policy
import cohesity_management_sdk.models_v2.aws_target_params_for_recover_s_3_buckets_or_objects

class RecoverAWSS3Params(object):

    """Implementation of the 'Recover AWS S3 params.' model.

    Specifies the parameters to recover AWS S3 Buckets.

    Attributes:
        aws_s_3_bucket_restore_filter_policy (AWSS3BucketRestoreFilterPolicy): Specifies the filtering policy for S3 Bucket restore.
        aws_target_params (AWSTargetParamsForRecoverS3BucketsOrObjects): Specifies the params for recovering to an AWS target.
        recover_protection_group_runs_params (string): Specifies the Protection Group Runs params to recover. All the
          VM's that are successfully backed up by specified Runs will be recovered.
          This can be specified along with individual snapshots of VMs. User has to
          make sure that specified Object snapshots and Protection Group Runs should
          not have any intersection. For example, user cannot specify multiple Runs
          which has same Object or an Object snapshot and a Run which has same Object's
          snapshot.
        target_environment (string): Specifies the environment of the recovery target. The corresponding
          params below must be filled out.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aws_s_3_bucket_restore_filter_policy":'awsS3BucketRestoreFilterPolicy',
        "aws_target_params":'awsTargetParams',
        "recover_protection_group_runs_params":'recoverProtectionGroupRunsParams',
        "target_environment":'targetEnvironment'
    }

    def __init__(self,
                 aws_s_3_bucket_restore_filter_policy=None,
                 aws_target_params=None,
                 recover_protection_group_runs_params=None,
                 target_environment='kAWS'):
        """Constructor for the RecoverAWSS3Params class"""

        # Initialize members of the class
        self.aws_s_3_bucket_restore_filter_policy = aws_s_3_bucket_restore_filter_policy
        self.aws_target_params = aws_target_params
        self.recover_protection_group_runs_params = recover_protection_group_runs_params
        self.target_environment = target_environment


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
        aws_s_3_bucket_restore_filter_policy = cohesity_management_sdk.models_v2.aws_s_3_bucket_restore_filter_policy.AWSS3BucketRestoreFilterPolicy.from_dictionary(
            dictionary.get('awsS3BucketRestoreFilterPolicy')) if dictionary.get('awsS3BucketRestoreFilterPolicy') else None
        aws_target_params = cohesity_management_sdk.models_v2.aws_target_params_for_recover_s_3_buckets_or_objects.AWSTargetParamsForRecoverS3BucketsOrObjects.from_dictionary(
            dictionary.get('awsTargetParams')) if dictionary.get('awsTargetParams') else None
        recover_protection_group_runs_params = dictionary.get('recoverProtectionGroupRunsParams')
        target_environment = dictionary.get('targetEnvironment')

        # Return an object of this model
        return cls(aws_s_3_bucket_restore_filter_policy,
                   aws_target_params,
                   recover_protection_group_runs_params,
                   target_environment)
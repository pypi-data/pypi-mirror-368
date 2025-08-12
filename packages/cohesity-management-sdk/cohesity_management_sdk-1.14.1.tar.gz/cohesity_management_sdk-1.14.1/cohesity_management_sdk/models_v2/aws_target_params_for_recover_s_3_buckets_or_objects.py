# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_recover_s_3_buckets_and_objects_new_target_config

class AWSTargetParamsForRecoverS3BucketsOrObjects(object):

    """Implementation of the 'AWSTargetParamsForRecoverS3BucketsOrObjects' model.

    Specifies the parameters for an AWS recovery target.

    Attributes:
        continue_on_error (bool): Specifies whether to continue restore on receiving error or not.
          Default is true.
        new_target_config (AWSRecoverS3BucketsAndObjectsNewTargetConfig): Specifies the configuration for recovering to a new target.
        object_prefix (string): Specifies the prefix to be added to all the objects being recovered.
        overwrite_existing (bool): Specifies whether to override the existing objects. Default is
          false.
        preserve_attributes (bool): Specifies whether to preserve the objects attributes at the time
          of restore. Default is true.
        recover_to_original_target (bool): Specifies whether to recover to the original target. If true,
          originalTargetConfig must be specified. If false, newTargetConfig must be
          specified.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "continue_on_error":'continueOnError',
        "new_target_config":'newTargetConfig',
        "object_prefix":'objectPrefix',
        "overwrite_existing":'overwriteExisting',
        "preserve_attributes":'preserveAttributes',
        "recover_to_original_target":'recoverToOriginalTarget'
    }

    def __init__(self,
                 continue_on_error=None,
                 new_target_config=None,
                 object_prefix=None,
                 overwrite_existing=None,
                 preserve_attributes=None,
                 recover_to_original_target=None):
        """Constructor for the AWSTargetParamsForRecoverS3BucketsOrObjects class"""

        # Initialize members of the class
        self.continue_on_error = continue_on_error
        self.new_target_config = new_target_config
        self.object_prefix = object_prefix
        self.overwrite_existing = overwrite_existing
        self.preserve_attributes = preserve_attributes
        self.recover_to_original_target = recover_to_original_target

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
        continue_on_error = dictionary.get('continueOnError')
        new_target_config = cohesity_management_sdk.models_v2.aws_recover_s_3_buckets_and_objects_new_target_config.AWSRecoverS3BucketsAndObjectsNewTargetConfig.from_dictionary(
            dictionary.get('newTargetConfig')) if dictionary.get('newTargetConfig') else None
        object_prefix = dictionary.get('objectPrefix')
        overwrite_existing = dictionary.get('overwriteExisting')
        preserve_attributes = dictionary.get('preserveAttributes')
        recover_to_original_target = dictionary.get('recoverToOriginalTarget')

        # Return an object of this model
        return cls(continue_on_error,
                   new_target_config,
                   object_prefix,
                   overwrite_existing,
                   preserve_attributes,
                   recover_to_original_target)
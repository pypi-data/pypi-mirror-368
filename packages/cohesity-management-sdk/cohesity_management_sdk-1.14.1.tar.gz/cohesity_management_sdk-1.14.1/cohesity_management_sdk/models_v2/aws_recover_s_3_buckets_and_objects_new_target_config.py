# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.target_vm_credentials

class AWSRecoverS3BucketsAndObjectsNewTargetConfig(object):

    """Implementation of the 'AWSRecoverS3BucketsAndObjectsNewTargetConfig' model.

    Specifies the configuration for recovering S3 objects and buckets
      to a new target.

    Attributes:
        bucket (RecoveryObjectIdentifier): Specifies the AWS bucket in which to recover S3 Objects.
        region (RecoveryObjectIdentifier): Specifies the AWS region in which to recover S3 Objects.
        source (RecoveryObjectIdentifier): Specifies the AWS account ID in which to recover S3 Objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "bucket":'bucket',
        "region":'region',
        "source":'source'
    }

    def __init__(self,
                 bucket=None,
                 region=None,
                 source=None):
        """Constructor for the AWSRecoverS3BucketsAndObjectsNewTargetConfig class"""

        # Initialize members of the class
        self.bucket = bucket
        self.region = region
        self.source = source


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
        bucket = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('bucket')) if dictionary.get('bucket') else None
        region = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('region')) if dictionary.get('region') else None
        source = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None

        # Return an object of this model
        return cls(bucket,
                   region,
                   source)
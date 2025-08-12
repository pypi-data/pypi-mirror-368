# -*- coding: utf-8 -*-


import cohesity_management_sdk.models_v2.retention
import cohesity_management_sdk.models_v2.aws_target_configuration
import cohesity_management_sdk.models_v2.azure_target_configuration

class ReplicationTargetConfiguration3(object):

    """Implementation of the 'Replication Target Configuration2' model.

    Specifies settings for copying Snapshots to cloud targets. This also
      specifies the retention policy that should be applied to Snapshots after they
      have been copied to the specified target.

    Attributes:
        retention (Retention): Specifies the Retention period of snapshot in days, months or
          years to retain copied Snapshots on the target.
        target_type (TargetType3Enum): Specifies the type of target to which replication need to be
          performed.
        aws_target (AWSTargetConfiguration): Specifies the config for AWS target.
           This must be specified if the target type is AWS.
        azure_target (AzureTargetConfiguration): Specifies the config for Azure target.
           This must be specified if the target type is Azure.
        on_legal_hold (bool): Specifies if the Run is on legal hold.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "retention":'retention',
        "target_type":'targetType',
        "aws_target":'awsTarget',
        "azure_target":'azureTarget',
        "on_legal_hold":'onLegalHold'
    }

    def __init__(self,
                 retention=None,
                 target_type=None,
                 aws_target=None,
                 azure_target=None,
                 on_legal_hold=None):
        """Constructor for the ReplicationTargetConfiguration3 class"""

        # Initialize members of the class
        self.retention = retention
        self.target_type = target_type
        self.aws_target = aws_target
        self.azure_target = azure_target
        self.on_legal_hold = on_legal_hold



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
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        target_type = dictionary.get('targetType')
        aws_target = cohesity_management_sdk.models_v2.aws_target_configuration.AWSTargetConfiguration.from_dictionary(dictionary.get('awsTarget')) if dictionary.get('awsTarget') else None
        azure_target = cohesity_management_sdk.models_v2.azure_target_configuration.AzureTargetConfiguration.from_dictionary(dictionary.get('azureTarget')) if dictionary.get('azureTarget') else None
        on_legal_hold = dictionary.get('onLegalHold')

        # Return an object of this model
        return cls(
                   retention,
                   target_type,
                   aws_target,
                   azure_target,
                   on_legal_hold)
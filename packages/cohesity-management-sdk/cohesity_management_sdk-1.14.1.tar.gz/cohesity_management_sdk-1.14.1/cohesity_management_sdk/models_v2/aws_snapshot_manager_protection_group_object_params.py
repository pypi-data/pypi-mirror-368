# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.ebs_volume_exclusion_params

class AWSSnapshotManagerProtectionGroupObjectParams(object):

    """Implementation of the 'AWS Snapshot Manager Protection Group Object Params.' model.

    Specifies the object parameters to create AWS Snapshot Manager Protection
      Group.

    Attributes:
        id (long|int): Specifies the id of the object.
        name (string): Specifies the name of the virtual machine.
        volume_exclusion_params (EbsVolumeExclusionParams): Specifies the paramaters to exclude volumes attached to EC2 instances
          at object level.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "volume_exclusion_params":'volumeExclusionParams'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 volume_exclusion_params=None):
        """Constructor for the AWSSnapshotManagerProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.volume_exclusion_params = volume_exclusion_params


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        volume_exclusion_params = cohesity_management_sdk.models_v2.ebs_volume_exclusion_params.EBSVolumeExclusionParams.from_dictionary(dictionary.get('volumeExclusionParams')) if dictionary.get('volumeExclusionParams') else None

        # Return an object of this model
        return cls(id,
                   name,
                   volume_exclusion_params)
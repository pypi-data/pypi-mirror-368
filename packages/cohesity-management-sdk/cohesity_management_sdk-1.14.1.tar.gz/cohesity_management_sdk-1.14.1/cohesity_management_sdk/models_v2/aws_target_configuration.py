# -*- coding: utf-8 -*-


class AWSTargetConfiguration(object):

    """Implementation of the 'AWS Target Configuration' model.

    Specifies the configuration for adding AWS as repilcation target

    Attributes:
        source_id (long|int): Specifies the source id of the AWS protection
            source registered on Cohesity cluster.
        name (string): Specifies the name of the AWS Replication target.
        region (long|int): Specifies id of the AWS region in which to
            replicate the Snapshot to. Applicable if replication target is AWS
            target.
        region_name (string): Specifies name of the AWS region in which to
            replicate the Snapshot to. Applicable if replication target is AWS
            target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_id":'sourceId',
        "region":'region',
        "name":'name',
        "region_name":'regionName'
    }

    def __init__(self,
                 source_id=None,
                 region=None,
                 name=None,
                 region_name=None):
        """Constructor for the AWSTargetConfiguration class"""

        # Initialize members of the class
        self.source_id = source_id
        self.name = name
        self.region = region
        self.region_name = region_name


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
        source_id = dictionary.get('sourceId')
        region = dictionary.get('region')
        name = dictionary.get('name')
        region_name = dictionary.get('regionName')

        # Return an object of this model
        return cls(source_id,
                   region,
                   name,
                   region_name)



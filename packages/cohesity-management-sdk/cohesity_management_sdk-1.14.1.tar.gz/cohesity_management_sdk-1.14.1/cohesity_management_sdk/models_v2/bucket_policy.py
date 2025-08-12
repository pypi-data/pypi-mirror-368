# -*- coding: utf-8 -*-


class BucketPolicy(object):

    """Implementation of the 'BucketPolicy' model.

    Specifies the policy in effect for this bucket..

    Attributes:
        id (string): Specifies the identifier of the bucket policy. This is a read-only
          property.
        raw_policy (string): Specifies the raw JSON string of the store policy.
        version (string): Specifies the language syntax rules that are to be used to process
          the policy. This is a read-only property.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "raw_policy":'rawPolicy',
        "version":'version'
    }

    def __init__(self,
                 id=None,
                 raw_policy=None,
                 version=None):
        """Constructor for the BucketPolicy class"""

        # Initialize members of the class
        self.id = id
        self.raw_policy = raw_policy
        self.version = version


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
        raw_policy = dictionary.get('rawPolicy')
        version = dictionary.get('version')

        # Return an object of this model
        return cls(id,
                   raw_policy,
                   version)
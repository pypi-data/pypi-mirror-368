# -*- coding: utf-8 -*-


class AWSS3BucketRestoreFilterPolicy(object):

    """Implementation of the 'AWSS3BucketRestoreFilterPolicy' model.

    Specifies the filtering policy for S3 Bucket Restore. This contains
      a list of include prefixes. If specified, only S3 Objects with a matching prefix
      will be recovered.

    Attributes:
        include_list (list of string): List of include prefixes that need to be recovered.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "include_list":'includeList'
    }

    def __init__(self,
                 include_list=None):
        """Constructor for the AWSS3BucketRestoreFilterPolicy class"""

        # Initialize members of the class
        self.include_list = include_list


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
        include_list = dictionary.get('includeList')

        # Return an object of this model
        return cls(include_list)
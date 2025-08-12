# -*- coding: utf-8 -*-


class S3OwnerInfo(object):

    """Implementation of the 'S3OwnerInfo' model.

    Specifies the owner info of an S3 bucket.

    Attributes:
        user_id (string): Specifies the user id of the owner.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "user_id":'userId'
    }

    def __init__(self,
                 user_id=None):
        """Constructor for the S3OwnerInfo class"""

        # Initialize members of the class
        self.user_id = user_id


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
        user_id = dictionary.get('userId')

        # Return an object of this model
        return cls(user_id)



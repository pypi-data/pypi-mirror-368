# -*- coding: utf-8 -*-


class OwnerInfo2(object):

    """Implementation of the 'OwnerInfo2' model.

    Specifies the owner info of the View as an S3 bucket.

    Attributes:
        distinguished_name (string): Specifies the distinguished name of the bucket owner for an ABAC
          enabled S3 Bucket.
        user_id (string): Specifies the user id of the owner.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "distinguished_name":'distinguishedName',
        "user_id":'userId'
    }

    def __init__(self,
                 distinguished_name=None,
                 user_id=None):
        """Constructor for the OwnerInfo2 class"""

        # Initialize members of the class
        self.distinguished_name = distinguished_name
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
        distinguished_name = dictionary.get('distinguishedName')
        user_id = dictionary.get('userId')

        # Return an object of this model
        return cls(distinguished_name,
                   user_id)
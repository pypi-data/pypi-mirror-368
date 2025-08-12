# -*- coding: utf-8 -*-


class AclGrantee(object):

    """Implementation of the 'AclGrantee' model.

    Specifies an ACL grantee.

    Attributes:
        mtype (string): Specifies the grantee type.
        user_id (string): Specifies the user id of the grantee.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "user_id":'userId'
    }

    def __init__(self,
                 mtype='RegisteredUser',
                 user_id=None):
        """Constructor for the AclGrantee class"""

        # Initialize members of the class
        self.mtype = mtype
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
        mtype = dictionary.get("type") if dictionary.get("type") else 'RegisteredUser'
        user_id = dictionary.get('userId')

        # Return an object of this model
        return cls(mtype,
                   user_id)



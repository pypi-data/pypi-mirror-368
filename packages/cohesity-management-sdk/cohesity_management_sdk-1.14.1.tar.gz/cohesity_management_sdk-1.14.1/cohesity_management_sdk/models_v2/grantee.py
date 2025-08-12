# -*- coding: utf-8 -*-


class Grantee(object):

    """Implementation of the 'Grantee' model.

    Specifies the grantee.

    Attributes:
        group (GroupEnum): Specifies the group to which permissions are granted if the `type`
          is Group.
        mtype (string): Specifies the grantee type.
        user_id (string): Specifies the user id of the grantee.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "group":'group',
        "mtype":'type',
        "user_id":'userId'
    }

    def __init__(self,
                 group=None,
                 mtype='RegisteredUser',
                 user_id=None):
        """Constructor for the Grantee class"""

        # Initialize members of the class
        self.group = group
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
        group = dictionary.get('group')
        mtype = dictionary.get("type") if dictionary.get("type") else 'RegisteredUser'
        user_id = dictionary.get('userId')

        # Return an object of this model
        return cls(group,
                   mtype,
                   user_id)
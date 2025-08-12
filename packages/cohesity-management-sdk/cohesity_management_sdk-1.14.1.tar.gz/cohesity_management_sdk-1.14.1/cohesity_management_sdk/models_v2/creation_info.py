# -*- coding: utf-8 -*-


class CreationInfo(object):

    """Implementation of the 'Creation Info' model.

    Specifies the information about the creation of the protection group or
    recovery.

    Attributes:
        user_name (string): Specifies the name of the user who created the
            protection group or recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "user_name":'userName'
    }

    def __init__(self,
                 user_name=None):
        """Constructor for the CreationInfo class"""

        # Initialize members of the class
        self.user_name = user_name


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
        user_name = dictionary.get('userName')

        # Return an object of this model
        return cls(user_name)



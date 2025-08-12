# -*- coding: utf-8 -*-


class User(object):

    """Implementation of the 'User' model.

    Specifies a user object.

    Attributes:
        name (string): Specifies the name of the user.
        sid (string): Specifies the sid of the user.
        domain (string): Specifies the domain of the user.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "sid":'sid',
        "domain":'domain'
    }

    def __init__(self,
                 name=None,
                 sid=None,
                 domain=None):
        """Constructor for the User class"""

        # Initialize members of the class
        self.name = name
        self.sid = sid
        self.domain = domain


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
        name = dictionary.get('name')
        sid = dictionary.get('sid')
        domain = dictionary.get('domain')

        # Return an object of this model
        return cls(name,
                   sid,
                   domain)



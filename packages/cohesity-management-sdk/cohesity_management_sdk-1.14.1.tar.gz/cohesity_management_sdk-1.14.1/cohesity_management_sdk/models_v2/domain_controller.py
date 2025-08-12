# -*- coding: utf-8 -*-


class DomainController(object):

    """Implementation of the 'DomainController' model.

    Specifies a domain controller.

    Attributes:
        name (string): Specifies the domain controller name.
        status (StatusEnum): Specifies the connection status.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "status":'status'
    }

    def __init__(self,
                 name=None,
                 status=None):
        """Constructor for the DomainController class"""

        # Initialize members of the class
        self.name = name
        self.status = status


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
        status = dictionary.get('status')

        # Return an object of this model
        return cls(name,
                   status)



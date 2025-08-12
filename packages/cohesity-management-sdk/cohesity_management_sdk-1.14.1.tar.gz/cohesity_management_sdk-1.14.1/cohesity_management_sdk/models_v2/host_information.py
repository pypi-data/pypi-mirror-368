# -*- coding: utf-8 -*-


class HostInformation(object):

    """Implementation of the 'HostInformation' model.

    Specifies the host information for a objects. This is mainly populated in
    case of App objects where app object is hosted by another object such as
    VM or physical server.

    Attributes:
        id (string): Specifies the id of the host object.
        name (string): Specifies the name of the host object.
        environment (EnvironmentEnum): Specifies the environment of the
            object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "environment":'environment'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 environment=None):
        """Constructor for the HostInformation class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.environment = environment


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
        name = dictionary.get('name')
        environment = dictionary.get('environment')

        # Return an object of this model
        return cls(id,
                   name,
                   environment)



# -*- coding: utf-8 -*-


class InterfaceRoleType(object):

    """Implementation of the 'Interface Role Type' model.

    Role of a network interface.

    Attributes:
        interface_role_type (InterfaceRoleType1Enum): Specifies the network
            interface role.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "interface_role_type":'interfaceRoleType'
    }

    def __init__(self,
                 interface_role_type=None):
        """Constructor for the InterfaceRoleType class"""

        # Initialize members of the class
        self.interface_role_type = interface_role_type


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
        interface_role_type = dictionary.get('interfaceRoleType')

        # Return an object of this model
        return cls(interface_role_type)



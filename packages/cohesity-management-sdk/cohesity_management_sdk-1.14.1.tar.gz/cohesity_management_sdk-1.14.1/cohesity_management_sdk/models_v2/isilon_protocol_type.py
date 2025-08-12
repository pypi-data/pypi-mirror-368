# -*- coding: utf-8 -*-


class IsilonProtocolType(object):

    """Implementation of the 'Isilon Protocol type.' model.

    Isilon Protocol type.

    Attributes:
        isilon_protocol (IsilonProtocolEnum): Specifies Isilon Protocol type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "isilon_protocol":'isilonProtocol'
    }

    def __init__(self,
                 isilon_protocol=None):
        """Constructor for the IsilonProtocolType class"""

        # Initialize members of the class
        self.isilon_protocol = isilon_protocol


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
        isilon_protocol = dictionary.get('isilonProtocol')

        # Return an object of this model
        return cls(isilon_protocol)



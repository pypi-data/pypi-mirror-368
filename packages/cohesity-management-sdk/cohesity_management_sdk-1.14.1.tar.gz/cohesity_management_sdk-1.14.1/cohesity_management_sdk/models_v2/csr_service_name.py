# -*- coding: utf-8 -*-


class CsrServiceName(object):

    """Implementation of the 'CsrServiceName' model.

    Csr Service Name

    Attributes:
        csr_service_name (CsrServiceName1Enum): Specifies the csr service
            name.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "csr_service_name":'csrServiceName'
    }

    def __init__(self,
                 csr_service_name=None):
        """Constructor for the CsrServiceName class"""

        # Initialize members of the class
        self.csr_service_name = csr_service_name


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
        csr_service_name = dictionary.get('csrServiceName')

        # Return an object of this model
        return cls(csr_service_name)



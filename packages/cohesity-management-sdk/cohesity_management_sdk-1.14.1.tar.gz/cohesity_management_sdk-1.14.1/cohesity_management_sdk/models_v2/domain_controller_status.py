# -*- coding: utf-8 -*-


class DomainControllerStatus(object):

    """Implementation of the 'Domain Controller Status' model.

    Connection status of domain controller.

    Attributes:
        domain_controller_status (DomainControllerStatus1Enum): Specifies the
            connection status of a domain controller.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_controller_status":'domainControllerStatus'
    }

    def __init__(self,
                 domain_controller_status=None):
        """Constructor for the DomainControllerStatus class"""

        # Initialize members of the class
        self.domain_controller_status = domain_controller_status


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
        domain_controller_status = dictionary.get('domainControllerStatus')

        # Return an object of this model
        return cls(domain_controller_status)



# -*- coding: utf-8 -*-


class DomainScopeParams(object):

    """Implementation of the 'DomainScopeParams' model.

    Specifies the parameters for domain type scope

    Attributes:
        domain_name (string): Specifies the domain name.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "domain_name":'domainName'
    }

    def __init__(self,
                 domain_name=None):
        """Constructor for the DomainScopeParams class"""

        # Initialize members of the class
        self.domain_name = domain_name


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
        domain_name = dictionary.get('domainName')

        # Return an object of this model
        return cls(domain_name)



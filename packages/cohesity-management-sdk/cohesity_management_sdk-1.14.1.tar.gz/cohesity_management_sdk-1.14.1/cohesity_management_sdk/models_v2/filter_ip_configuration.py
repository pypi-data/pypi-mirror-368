# -*- coding: utf-8 -*-


class FilterIPConfiguration(object):

    """Implementation of the 'Filter IP Configuration' model.

    Specifies the list of IP addresses that are allowed or denied during
    recovery. Allowed IPs and Denied IPs cannot be used together.

    Attributes:
        denied_ip_addresses (list of string): Specifies the IP addresses that
            should not be used during recovery recovery. Cannot be set if
            allowedIpAddresses is set.
        allowed_ip_addresses (list of string): Specifies the IP addresses that
            should be used exclusively during recovery. Cannot be set if
            deniedIpAddresses is set.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "denied_ip_addresses":'deniedIpAddresses',
        "allowed_ip_addresses":'allowedIpAddresses'
    }

    def __init__(self,
                 denied_ip_addresses=None,
                 allowed_ip_addresses=None):
        """Constructor for the FilterIPConfiguration class"""

        # Initialize members of the class
        self.denied_ip_addresses = denied_ip_addresses
        self.allowed_ip_addresses = allowed_ip_addresses


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
        denied_ip_addresses = dictionary.get('deniedIpAddresses')
        allowed_ip_addresses = dictionary.get('allowedIpAddresses')

        # Return an object of this model
        return cls(denied_ip_addresses,
                   allowed_ip_addresses)



# -*- coding: utf-8 -*-


class MachineAccount(object):

    """Implementation of the 'MachineAccount' model.

    Specifies a machine account.

    Attributes:
        name (string): Specifies the machine account name.
        dns_host_name (string): Specifies the DNS host name of the machine
            account.
        encryption (list of EncryptionEnum): Specifies a list of encryption
            types apply to the machine account.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "dns_host_name":'dnsHostName',
        "encryption":'encryption'
    }

    def __init__(self,
                 name=None,
                 dns_host_name=None,
                 encryption=None):
        """Constructor for the MachineAccount class"""

        # Initialize members of the class
        self.name = name
        self.dns_host_name = dns_host_name
        self.encryption = encryption


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
        dns_host_name = dictionary.get('dnsHostName')
        encryption = dictionary.get('encryption')

        # Return an object of this model
        return cls(name,
                   dns_host_name,
                   encryption)



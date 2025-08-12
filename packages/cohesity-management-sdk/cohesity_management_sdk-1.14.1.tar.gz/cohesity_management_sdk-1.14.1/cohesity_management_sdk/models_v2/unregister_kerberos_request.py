# -*- coding: utf-8 -*-


class UnregisterKerberosRequest(object):

    """Implementation of the 'UnregisterKerberosRequest' model.

    Specifies the request to unregister a Kerberos Provider.

    Attributes:
        admin_password (string): Specifies the password

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "admin_password":'adminPassword'
    }

    def __init__(self,
                 admin_password=None):
        """Constructor for the UnregisterKerberosRequest class"""

        # Initialize members of the class
        self.admin_password = admin_password


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
        admin_password = dictionary.get('adminPassword')

        # Return an object of this model
        return cls(admin_password)



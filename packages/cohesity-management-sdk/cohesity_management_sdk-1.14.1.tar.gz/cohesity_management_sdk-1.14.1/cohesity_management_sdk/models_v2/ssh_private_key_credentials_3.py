# -*- coding: utf-8 -*-


class SshPrivateKeyCredentials3(object):

    """Implementation of the 'SshPrivateKeyCredentials3' model.

    SSH  userID + privateKey required for reading configuration file.

    Attributes:
        passphrase (string): Passphrase for the private key.
        private_key (string): The private key.
        user_id (string): userId for PrivateKey credentials.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "private_key":'privateKey',
        "user_id":'userId',
        "passphrase":'passphrase'
    }

    def __init__(self,
                 private_key=None,
                 user_id=None,
                 passphrase=None):
        """Constructor for the SshPrivateKeyCredentials3 class"""

        # Initialize members of the class
        self.passphrase = passphrase
        self.private_key = private_key
        self.user_id = user_id


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
        private_key = dictionary.get('privateKey')
        user_id = dictionary.get('userId')
        passphrase = dictionary.get('passphrase')

        # Return an object of this model
        return cls(private_key,
                   user_id,
                   passphrase)



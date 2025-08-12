# -*- coding: utf-8 -*-


class PrivateKeyCredentials(object):

    """Implementation of the 'Private key credentials' model.

    Specifies the credentials for certificate based authentication.

    Attributes:
        user_id (string): Specifies the userId to access target entity.
        private_key (string): Specifies the private key to access target
            entity.
        passphrase (string): Specifies the passphrase to access target
            entity.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "user_id":'userId',
        "private_key":'privateKey',
        "passphrase":'passphrase'
    }

    def __init__(self,
                 user_id=None,
                 private_key=None,
                 passphrase=None):
        """Constructor for the PrivateKeyCredentials class"""

        # Initialize members of the class
        self.user_id = user_id
        self.private_key = private_key
        self.passphrase = passphrase


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
        user_id = dictionary.get('userId')
        private_key = dictionary.get('privateKey')
        passphrase = dictionary.get('passphrase')

        # Return an object of this model
        return cls(user_id,
                   private_key,
                   passphrase)



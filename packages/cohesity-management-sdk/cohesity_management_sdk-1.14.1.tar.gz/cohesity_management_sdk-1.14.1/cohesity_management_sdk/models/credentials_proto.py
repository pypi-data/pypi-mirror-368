# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class CredentialsProto(object):

    """Implementation of the 'CredentialsProto' model.

    Copied from: base/credentials.proto -> message Credentials.

    Attributes:
        encrypted_password (list of int): AES256 encrypted password. The key
            for encryption should be obtained from KMS. This field stores the
            encrypted password when the credentials are being sent to bifrost.
        password (list of int): This field is not used in storage, other than
            historical records.
            The field is only set for inflight rpcs.
        token (string): The token to use for authentication. For example, in a
            SAN environment,
            this can be the API token that is used to create a REST session
        username (string): The username and password to use for authentication.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "encrypted_password":'encryptedPassword',
        "password":'password',
        "token":'token',
        "username":'username'
    }

    def __init__(self,
                 encrypted_password=None,
                 password=None,
                 token=None,
                 username=None):
        """Constructor for the CredentialsProto class"""

        # Initialize members of the class
        self.encrypted_password = encrypted_password
        self.password = password
        self.token = token
        self.username = username


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
        encrypted_password = dictionary.get('encryptedPassword')
        password = dictionary.get('password')
        token = dictionary.get('token')
        username = dictionary.get('username')

        # Return an object of this model
        return cls(encrypted_password,
                   password,
                   token,
                   username)



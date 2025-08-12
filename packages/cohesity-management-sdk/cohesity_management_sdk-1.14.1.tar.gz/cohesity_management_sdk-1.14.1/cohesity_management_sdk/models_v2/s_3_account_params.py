# -*- coding: utf-8 -*-


class S3AccountParams(object):

    """Implementation of the 'S3AccountParams' model.

    Specifies S3 Account parameters for User.

    Attributes:
        s_3_access_key_id (string): Specifies the S3 Account Access Key ID.
        s_3_account_id (string): Specifies the S3 Account Canonical User ID.
        s_3_secret_key (string): Specifies the S3 Account Secret Key.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "s_3_access_key_id":'s3AccessKeyId',
        "s_3_account_id":'s3AccountId',
        "s_3_secret_key":'s3SecretKey'
    }

    def __init__(self,
                 s_3_access_key_id=None,
                 s_3_account_id=None,
                 s_3_secret_key=None):
        """Constructor for the S3AccountParams class"""

        # Initialize members of the class
        self.s_3_access_key_id = s_3_access_key_id
        self.s_3_account_id = s_3_account_id
        self.s_3_secret_key = s_3_secret_key

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
        s_3_access_key_id = dictionary.get('s3AccessKeyId')
        s_3_account_id = dictionary.get('s3AccountId')
        s_3_secret_key = dictionary.get('s3SecretKey')

        # Return an object of this model
        return cls(s_3_access_key_id,
                   s_3_account_id,
                   s_3_secret_key)
# -*- coding: utf-8 -*-


class AWSIAMUsercredentialsrequestparameters(object):

    """Implementation of the 'AWSIAMUsercredentialsrequestparameters' model.

    Specifies the credentials to register a commercial AWS

    Attributes:
        access_key (string): Specifies Access key of the AWS account.
        arn (string): Specifies Amazon Resource Name (owner ID) of the IAM user, acts
          as an unique identifier of as AWS entity.
        secret_access_key (string): Specifies Secret Access key of the AWS account.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "access_key":'accessKey',
        "arn":'arn',
        "secret_access_key":'secretAccessKey'
    }

    def __init__(self,
                 access_key=None,
                 arn=None,
                 secret_access_key=None):
        """Constructor for the AWSIAMUsercredentialsrequestparameters class"""

        # Initialize members of the class
        self.access_key = access_key
        self.arn = arn
        self.secret_access_key = secret_access_key


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
        access_key = dictionary.get('accessKey')
        arn = dictionary.get('arn')
        secret_access_key= dictionary.get('secretAccessKey')

        # Return an object of this model
        return cls(access_key,
                   arn,
                   secret_access_key)
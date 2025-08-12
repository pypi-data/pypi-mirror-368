# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_iam_role_credentials_request_parameters
import cohesity_management_sdk.models_v2.aws_iam_user_credentials_request_parameters

class RegisterAWSCommercialrequestparameters(object):

    """Implementation of the 'RegisterAWSCommercialrequestparameters' model.

    Specifies the parameters to register a commercial AWS

    Attributes:
        auth_method_type (AuthMethodTypeEnum): Specifies the Authentication method(IamArn/IamRole)
             used by api
        iam_role_aws_credentials (IamRoleAwsCredentials): Specifies the credentials required
            to register as AWS source.
        iam_user_aws_credentials (IamUserAwsCredentials): Specifies the credentials required to
            register as AWS source.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "auth_method_type":'authMethodType',
        "iam_role_aws_credentials":'iamRoleAwsCredentials',
        "iam_user_aws_credentials":'iamUserAwsCredentials'
    }

    def __init__(self,
                 auth_method_type=None,
                 iam_role_aws_credentials=None,
                 iam_user_aws_credentials=None):
        """Constructor for the RegisterAWSCommercialrequestparameters class"""

        # Initialize members of the class
        self.auth_method_type = auth_method_type
        self.iam_role_aws_credentials = iam_role_aws_credentials
        self.iam_user_aws_credentials = iam_user_aws_credentials


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
        auth_method_type = dictionary.get('authMethodType')
        iam_role_aws_credentials = cohesity_management_sdk.models_v2.aws_iam_role_credentials_request_parameters.AWSIAMRolecredentialsrequestparameters.from_dictionary(dictionary.get('iamRoleAwsCredentials'))
        iam_user_aws_credentials = cohesity_management_sdk.models_v2.aws_iam_user_credentials_request_parameters.AWSIAMUsercredentialsrequestparameters.from_dictionary(dictionary.get('iamUserAwsCredentials'))

        # Return an object of this model
        return cls(auth_method_type,
                   iam_role_aws_credentials,
                   iam_user_aws_credentials)
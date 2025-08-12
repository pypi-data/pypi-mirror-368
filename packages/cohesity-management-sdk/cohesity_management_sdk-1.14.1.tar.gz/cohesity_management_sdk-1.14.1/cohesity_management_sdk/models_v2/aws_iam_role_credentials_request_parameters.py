# -*- coding: utf-8 -*-


class AWSIAMRolecredentialsrequestparameters(object):

    """Implementation of the 'AWS IAM Role credentials request parameters.' model.

    Specifies the credentials to register a commercial AWS

    Attributes:
        cp_iam_role_arn (string): This is only applicable in case of DMaaS.
          Control plane IAM role ARN, this is first assumed by the dataplane(cluster).
          Then we assume the iam_role_arn which is tenant's IAM role with all required
          permissions.
        iam_role_arn (string): Specifies the IAM role which will be used to access the security
          credentials required for API calls. This should have all the permissions
          required for the tenant's use case. In case of DMaaS this will be the Tenant's
          IAM role ARN. This is assumed only after the cp_iam_role_arn(control plane
          role) is assumed

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cp_iam_role_arn":'cpIamRoleArn',
        "iam_role_arn":'iamRoleArn'
    }

    def __init__(self,
                 cp_iam_role_arn=None,
                 iam_role_arn=None):
        """Constructor for the AWSIAMRolecredentialsrequestparameters class"""

        # Initialize members of the class
        self.cp_iam_role_arn = cp_iam_role_arn
        self.iam_role_arn = iam_role_arn


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
        cp_iam_role_arn = dictionary.get('cpIamRoleArn')
        iam_role_arn = dictionary.get('iamRoleArn')

        # Return an object of this model
        return cls(cp_iam_role_arn,
                   iam_role_arn)
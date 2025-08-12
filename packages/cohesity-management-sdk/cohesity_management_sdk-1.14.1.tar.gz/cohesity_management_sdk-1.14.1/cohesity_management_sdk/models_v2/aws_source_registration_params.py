# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_s_3_source_register_parameters
import cohesity_management_sdk.models_v2.register_aws_commercial_request_parameters

class AwsSourceRegistrationParams(object):

    """Implementation of the 'AwsSourceRegistrationParams' model.

    Specifies the paramaters to register an AWS source.

    Attributes:
        s3_params (AWS_S_3sourceregisterparameters): Specifies the s3 specific parameters for
              source registration.
        standard_params (RegisterAWSCommercialrequestparameters): Specifies the parameters to register a commercial AWS.
        subscription_type (SubscriptionTypeEnum): Specifies the AWS Subscription type (Commercial/Gov).
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "s3_params":'s3Params',
        "standard_params":'standardParams',
        "subscription_type":'subscriptionType'
    }

    def __init__(self,
                 s3_params=None,
                 standard_params=None,
                 subscription_type=None):
        """Constructor for the AwsSourceRegistrationParams class"""

        # Initialize members of the class
        self.s3_params = s3_params
        self.standard_params = standard_params
        self.subscription_type = subscription_type


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
        s3_params = cohesity_management_sdk.models_v2.aws_s_3_source_register_parameters.AWS_S3sourceregisterparameters.from_dictionary(dictionary.get('s3Params'))
        standard_params = cohesity_management_sdk.models_v2.register_aws_commercial_request_parameters.RegisterAWSCommercialrequestparameters.from_dictionary(
            dictionary.get('standardParams'))
        subscription_type = dictionary.get('subscriptionType')

        # Return an object of this model
        return cls(s3_params,
                   standard_params,
                   subscription_type)
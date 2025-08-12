# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_parameters
import cohesity_management_sdk.models_v2.azure_parameters

class CloudSpinTarget(object):

    """Implementation of the 'CloudSpinTarget' model.

    Specifies the details about Cloud Spin target where backup snapshots may
    be converted and stored.

    Attributes:
        id (long|int): Specifies the unique id of the cloud spin entity.
        aws_params (AWSParameters): Specifies various resources when
            converting and deploying a VM to AWS.
        azure_params (AzureParameters): Specifies various resources when
            converting and deploying a VM to Azure.
        name (string): Specifies the name of the already added cloud spin
            target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "aws_params":'awsParams',
        "azure_params":'azureParams',
        "name":'name'
    }

    def __init__(self,
                 id=None,
                 aws_params=None,
                 azure_params=None,
                 name=None):
        """Constructor for the CloudSpinTarget class"""

        # Initialize members of the class
        self.id = id
        self.aws_params = aws_params
        self.azure_params = azure_params
        self.name = name


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
        id = dictionary.get('id')
        aws_params = cohesity_management_sdk.models_v2.aws_parameters.AWSParameters.from_dictionary(dictionary.get('awsParams')) if dictionary.get('awsParams') else None
        azure_params = cohesity_management_sdk.models_v2.azure_parameters.AzureParameters.from_dictionary(dictionary.get('azureParams')) if dictionary.get('azureParams') else None
        name = dictionary.get('name')

        # Return an object of this model
        return cls(id,
                   aws_params,
                   azure_params,
                   name)



# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.custom_tag_params


class AWSParameters(object):

    """Implementation of the 'AWS Parameters.' model.

    Specifies various resources when converting and deploying a VM to AWS.

    Attributes:
        custom_tag_list (list of CustomTagParams): Specifies tags of various resources when converting and deploying
          a VM to AWS.
        region (long|int): Specifies id of the AWS region in which to deploy
            the VM.
        subnet_id (long|int): Specifies id of the subnet within above VPC.
        vpc_id (long|int): Specifies id of the Virtual Private Cloud to chose
            for the instance type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "custom_tag_list":'customTagList',
        "region":'region',
        "subnet_id":'subnetId',
        "vpc_id":'vpcId',
    }

    def __init__(self,
                 custom_tag_list=None,
                 region=None,
                 subnet_id=None,
                 vpc_id=None,):
        """Constructor for the AWSParameters class"""

        # Initialize members of the class
        self.custom_tag_list = custom_tag_list
        self.region = region
        self.subnet_id = subnet_id
        self.vpc_id = vpc_id


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
        custom_tag_list = None
        if dictionary.get("customTagList") is not None:
            custom_tag_list = list()
            for structure in dictionary.get('customTagList'):
                custom_tag_list.append(cohesity_management_sdk.models_v2.custom_tag_params.CustomTagParams.from_dictionary(structure))
        region = dictionary.get('region')
        subnet_id = dictionary.get('subnetId')
        vpc_id = dictionary.get('vpcId')

        # Return an object of this model
        return cls(custom_tag_list,
                   region,
                   subnet_id,
                   vpc_id,)
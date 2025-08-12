# -*- coding: utf-8 -*-


class UpdateFleetEnvInfoRequest(object):

    """Implementation of the 'Update Fleet Env Info Request.' model.

    Specifies the params to add fleet env info.

    Attributes:
        iam_role (string): Specifies the IAM role used to create instances.
        region (string): Specifies the Region of the CE cluster.
        vpc_id (string): Specifies the VPC of the CE cluster.
        subnet_id (string): Specifies the Subnet of the CE cluster.
        security_group_id (string): Specifies the security group Id.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "iam_role":'iamRole',
        "region":'region',
        "vpc_id":'vpcId',
        "subnet_id":'subnetId',
        "security_group_id":'securityGroupId'
    }

    def __init__(self,
                 iam_role=None,
                 region=None,
                 vpc_id=None,
                 subnet_id=None,
                 security_group_id=None):
        """Constructor for the UpdateFleetEnvInfoRequest class"""

        # Initialize members of the class
        self.iam_role = iam_role
        self.region = region
        self.vpc_id = vpc_id
        self.subnet_id = subnet_id
        self.security_group_id = security_group_id


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
        iam_role = dictionary.get('iamRole')
        region = dictionary.get('region')
        vpc_id = dictionary.get('vpcId')
        subnet_id = dictionary.get('subnetId')
        security_group_id = dictionary.get('securityGroupId')

        # Return an object of this model
        return cls(iam_role,
                   region,
                   vpc_id,
                   subnet_id,
                   security_group_id)



# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vpc
import cohesity_management_sdk.models_v2.subnet_1
import cohesity_management_sdk.models_v2.recovery_object_identifier

class NetworkConfig3(object):

    """Implementation of the 'NetworkConfig3' model.

    Specifies the networking configuration to be applied to the recovered
    VMs.

    Attributes:
        vpc (Vpc): Specifies the Virtual Private Cloud to choose for the
            instance type.
        subnet (Subnet1): Specifies the subnet within above VPC.
        security_groups (list of RecoveryObjectIdentifier): Specifies the
            network security groups within above VPC.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vpc":'vpc',
        "subnet":'subnet',
        "security_groups":'securityGroups'
    }

    def __init__(self,
                 vpc=None,
                 subnet=None,
                 security_groups=None):
        """Constructor for the NetworkConfig3 class"""

        # Initialize members of the class
        self.vpc = vpc
        self.subnet = subnet
        self.security_groups = security_groups


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
        vpc = cohesity_management_sdk.models_v2.vpc.Vpc.from_dictionary(dictionary.get('vpc')) if dictionary.get('vpc') else None
        subnet = cohesity_management_sdk.models_v2.subnet_1.Subnet1.from_dictionary(dictionary.get('subnet')) if dictionary.get('subnet') else None
        security_groups = None
        if dictionary.get("securityGroups") is not None:
            security_groups = list()
            for structure in dictionary.get('securityGroups'):
                security_groups.append(cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(structure))

        # Return an object of this model
        return cls(vpc,
                   subnet,
                   security_groups)



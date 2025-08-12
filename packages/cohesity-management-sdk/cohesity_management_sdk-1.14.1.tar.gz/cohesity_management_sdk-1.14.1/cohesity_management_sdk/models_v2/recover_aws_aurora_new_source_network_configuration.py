# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vpc
import cohesity_management_sdk.models_v2.subnet_1
import cohesity_management_sdk.models_v2.availability_zone
import cohesity_management_sdk.models_v2.recovery_object_identifier

class RecoverAWSAuroraNewSourceNetworkConfiguration(object):

    """Implementation of the 'Recover AWS Aurora New Source Network configuration.' model.

    Specifies the network config parameters to be applied for AWS Aurora if
    recovering to new Source.

    Attributes:
        vpc (Vpc): Specifies the Virtual Private Cloud to choose for the
            instance type.
        subnet (Subnet1): Specifies the subnet within above VPC.
        availability_zone (AvailabilityZone): Specifies the entity
            representing the availability zone to use while restoring the DB.
        security_groups (list of RecoveryObjectIdentifier): Specifies the
            network security groups within above VPC.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vpc":'vpc',
        "subnet":'subnet',
        "availability_zone":'availabilityZone',
        "security_groups":'securityGroups'
    }

    def __init__(self,
                 vpc=None,
                 subnet=None,
                 availability_zone=None,
                 security_groups=None):
        """Constructor for the RecoverAWSAuroraNewSourceNetworkConfiguration class"""

        # Initialize members of the class
        self.vpc = vpc
        self.subnet = subnet
        self.availability_zone = availability_zone
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
        availability_zone = cohesity_management_sdk.models_v2.availability_zone.AvailabilityZone.from_dictionary(dictionary.get('availabilityZone')) if dictionary.get('availabilityZone') else None
        security_groups = None
        if dictionary.get("securityGroups") is not None:
            security_groups = list()
            for structure in dictionary.get('securityGroups'):
                security_groups.append(cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(structure))

        # Return an object of this model
        return cls(vpc,
                   subnet,
                   availability_zone,
                   security_groups)



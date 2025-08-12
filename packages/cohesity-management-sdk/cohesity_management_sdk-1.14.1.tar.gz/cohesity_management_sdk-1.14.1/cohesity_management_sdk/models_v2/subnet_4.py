# -*- coding: utf-8 -*-


class Subnet4(object):

    """Implementation of the 'Subnet4' model.

    Specifies the subnet.

    Attributes:
        subnet_id (long|int): Specifies the id of the subnet.
        subnet_name (string): Specifies the name of the subnet.
        vpc_name (string): Specifies the name of the vpc network.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "subnet_id":'subnetId',
        "subnet_name":'subnetName',
        "vpc_name":'vpcName'
    }

    def __init__(self,
                 subnet_id=None,
                 subnet_name=None,
                 vpc_name=None):
        """Constructor for the Subnet4 class"""

        # Initialize members of the class
        self.subnet_id = subnet_id
        self.subnet_name = subnet_name
        self.vpc_name = vpc_name


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
        subnet_id = dictionary.get('subnetId')
        subnet_name = dictionary.get('subnetName')
        vpc_name = dictionary.get('vpcName')

        # Return an object of this model
        return cls(subnet_id,
                   subnet_name,
                   vpc_name)



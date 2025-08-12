# -*- coding: utf-8 -*-


class OracleProtectionGroupVlanInfo(object):

    """Implementation of the 'Oracle Protection Group vlan info' model.

    Specifies details about capturing Cohesity cluster VLAN info for Oracle
    workflow.

    Attributes:
        ip_list (list of string): Specifies the list of Ips in this VLAN.
        gateway (string): Specifies the gateway of this VLAN.
        id (int): Specifies the Id of this VLAN.
        subnet_ip (string): Specifies the subnet Ip for this VLAN.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ip_list":'ipList',
        "gateway":'gateway',
        "id":'id',
        "subnet_ip":'subnetIp'
    }

    def __init__(self,
                 ip_list=None,
                 gateway=None,
                 id=None,
                 subnet_ip=None):
        """Constructor for the OracleProtectionGroupVlanInfo class"""

        # Initialize members of the class
        self.ip_list = ip_list
        self.gateway = gateway
        self.id = id
        self.subnet_ip = subnet_ip


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
        ip_list = dictionary.get('ipList')
        gateway = dictionary.get('gateway')
        id = dictionary.get('id')
        subnet_ip = dictionary.get('subnetIp')

        # Return an object of this model
        return cls(ip_list,
                   gateway,
                   id,
                   subnet_ip)



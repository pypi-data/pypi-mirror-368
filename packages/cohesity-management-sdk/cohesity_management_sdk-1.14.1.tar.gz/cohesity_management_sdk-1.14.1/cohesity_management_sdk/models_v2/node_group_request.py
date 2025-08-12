# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.bgp_instance
import cohesity_management_sdk.models_v2.subnet_info
import cohesity_management_sdk.models_v2.dns_servers_info

class NodeGroupRequest(object):

    """Implementation of the 'Node Group Request.' model.

    Specifies the request to create a Node Group.

    Attributes:
        name (string): Specifies the name of the Node Group.
        node_ids (list of long|int): List of Node Ids that are part of this
            node group.
        id (int): Id of the node group.
        mtype (int): Type of the node group.
        bgp_instance (BgpInstance): BGP instance.
        subnet_info (SubnetInfo): Subnet information.
        dns_servers_info (DnsServersInfo): List of DNS servers in cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "node_ids":'node-ids',
        "id":'id',
        "mtype":'type',
        "bgp_instance":'bgpInstance',
        "subnet_info":'subnetInfo',
        "dns_servers_info":'dnsServersInfo'
    }

    def __init__(self,
                 name=None,
                 node_ids=None,
                 id=None,
                 mtype=None,
                 bgp_instance=None,
                 subnet_info=None,
                 dns_servers_info=None):
        """Constructor for the NodeGroupRequest class"""

        # Initialize members of the class
        self.name = name
        self.node_ids = node_ids
        self.id = id
        self.mtype = mtype
        self.bgp_instance = bgp_instance
        self.subnet_info = subnet_info
        self.dns_servers_info = dns_servers_info


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
        name = dictionary.get('name')
        node_ids = dictionary.get('node-ids')
        id = dictionary.get('id')
        mtype = dictionary.get('type')
        bgp_instance = cohesity_management_sdk.models_v2.bgp_instance.BgpInstance.from_dictionary(dictionary.get('bgpInstance')) if dictionary.get('bgpInstance') else None
        subnet_info = cohesity_management_sdk.models_v2.subnet_info.SubnetInfo.from_dictionary(dictionary.get('subnetInfo')) if dictionary.get('subnetInfo') else None
        dns_servers_info = cohesity_management_sdk.models_v2.dns_servers_info.DnsServersInfo.from_dictionary(dictionary.get('dnsServersInfo')) if dictionary.get('dnsServersInfo') else None

        # Return an object of this model
        return cls(name,
                   node_ids,
                   id,
                   mtype,
                   bgp_instance,
                   subnet_info,
                   dns_servers_info)



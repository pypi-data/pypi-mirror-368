# -*- coding: utf-8 -*-


class VlanConfig1(object):

    """Implementation of the 'VlanConfig1' model.

    Specifies VLAN Params associated with the recovered. If this is not
    specified, then the VLAN settings will be automatically selected from one
    of the below options: a. If VLANs are configured on Cohesity, then the
    VLAN host/VIP will be automatically based on the client's (e.g. ESXI host)
    IP address. b. If VLANs are not configured on Cohesity, then the partition
    hostname or VIPs will be used for Recovery.

    Attributes:
        id (int): If this is set, then the Cohesity host name or the IP
            address associated with this vlan is used for mounting Cohesity's
            view on the remote host.
        disable_vlan (bool): If this is set to true, then even if VLANs are
            configured on the system, the partition VIPs will be used for the
            Recovery.
        interface_name (string): Interface group to use for Recovery.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "disable_vlan":'disableVlan',
        "interface_name":'interfaceName'
    }

    def __init__(self,
                 id=None,
                 disable_vlan=None,
                 interface_name=None):
        """Constructor for the VlanConfig1 class"""

        # Initialize members of the class
        self.id = id
        self.disable_vlan = disable_vlan
        self.interface_name = interface_name


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
        disable_vlan = dictionary.get('disableVlan')
        interface_name = dictionary.get('interfaceName')

        # Return an object of this model
        return cls(id,
                   disable_vlan,
                   interface_name)



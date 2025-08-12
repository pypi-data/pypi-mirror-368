# -*- coding: utf-8 -*-


class VlanParamsForBackupRestoreOperation(object):

    """Implementation of the 'Vlan Params for backup/restore operation.' model.

    Specifies VLAN params associated with the backup/restore operation.

    Attributes:
        vlan_id (int): If this is set, then the Cohesity host name or the IP
            address associated with this VLAN is used for mounting Cohesity's
            view on the remote host.
        disable_vlan (bool): If this is set to true, then even if VLANs are
            configured on the system, the partition VIPs will be used for the
            restore.
        interface_name (string): Interface group to use for backup/restore. If
            this is not specified, primary interface group for the cluster
            will be used.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vlan_id":'vlanId',
        "disable_vlan":'disableVlan',
        "interface_name":'interfaceName'
    }

    def __init__(self,
                 vlan_id=None,
                 disable_vlan=None,
                 interface_name=None):
        """Constructor for the VlanParamsForBackupRestoreOperation class"""

        # Initialize members of the class
        self.vlan_id = vlan_id
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
        vlan_id = dictionary.get('vlanId')
        disable_vlan = dictionary.get('disableVlan')
        interface_name = dictionary.get('interfaceName')

        # Return an object of this model
        return cls(vlan_id,
                   disable_vlan,
                   interface_name)



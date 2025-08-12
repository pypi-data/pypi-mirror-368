# -*- coding: utf-8 -*-


class Subnet(object):

    """Implementation of the 'Subnet' model.

    Defines a Subnet (Subnetwork).
    The netmask can be specified by setting netmaskBits or netmaskIp4.
    The netmask can only be set using netmaskIp4 if the IP address
    is an IPv4 address.

    Attributes:
        component (string): Component that has reserved the subnet.
        description (string): Description of the subnet.
        gateway (string): Gateway for the subnet.
        id (int): ID of the subnet.
        ip (string): Specifies either an IPv6 address or an IPv4 address.
        netmask_bits (int): Specifies the netmask using bits.
        netmask_ip_4 (string): Specifies the netmask using an IP4 address. The
            netmask can only be set using netmaskIp4 if the IP address is an
            IPv4 address.
        nfs_access (NfsAccessEnum): Specifies whether clients from this subnet
            can mount using NFS protocol. Protocol access level. 'kDisabled'
            indicates Protocol access level 'Disabled' 'kReadOnly' indicates
            Protocol access level 'ReadOnly' 'kReadWrite' indicates Protocol
            access level 'ReadWrite'
        nfs_squash (NfsSquashEnum): Specifies which nfsSquash Mounted. 'kNone'
            mounts none. 'kRootSquash' mounts nfsRootSquash. Whether clients
            from this subnet can mount as root on NFS. 'kAllSquash' mounts
            nfsAllSquash. Whether all clients from this subnet can map view
            with view_all_squash_uid/view_all_squash_gid configured in the
            view.
        s_3_access (s3AccessEnum): Specifies whether clients from this subnet can access using
          S3 protocol.
          Protocol access level.
          kDisabled indicates Protocol access level 'Disabled'
          kReadOnly indicates Protocol access level 'ReadOnly'
          kReadWrite indicates Protocol access level 'ReadWrite'
        smb_access (SmbAccessEnum): Specifies whether clients from this subnet
            can mount using SMB protocol. Protocol access level. 'kDisabled'
            indicates Protocol access level 'Disabled' 'kReadOnly' indicates
            Protocol access level 'ReadOnly' 'kReadWrite' indicates Protocol
            access level 'ReadWrite'

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "component":'component',
        "description":'description',
        "gateway":'gateway',
        "id":'id',
        "ip":'ip',
        "netmask_bits":'netmaskBits',
        "netmask_ip_4":'netmaskIp4',
        "nfs_access":'nfsAccess',
        "nfs_squash":'nfsSquash',
        "s_3_access":'s3Access',
        "smb_access":'smbAccess'
    }

    def __init__(self,
                 component=None,
                 description=None,
                 gateway=None,
                 id=None,
                 ip=None,
                 netmask_bits=None,
                 netmask_ip_4=None,
                 nfs_access=None,
                 nfs_squash=None,
                 s_3_access=None,
                 smb_access=None):
        """Constructor for the Subnet class"""

        # Initialize members of the class
        self.component = component
        self.description = description
        self.gateway = gateway
        self.id = id
        self.ip = ip
        self.netmask_bits = netmask_bits
        self.netmask_ip_4 = netmask_ip_4
        self.nfs_access = nfs_access
        self.nfs_squash = nfs_squash
        self.s_3_access = s_3_access
        self.smb_access = smb_access


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
        component = dictionary.get('component')
        description = dictionary.get('description')
        gateway = dictionary.get('gateway')
        id = dictionary.get('id')
        ip = dictionary.get('ip')
        netmask_bits = dictionary.get('netmaskBits')
        netmask_ip_4 = dictionary.get('netmaskIp4')
        nfs_access = dictionary.get('nfsAccess')
        nfs_squash = dictionary.get('nfsSquash')
        s_3_access = dictionary.get('s3Access')
        smb_access = dictionary.get('smbAccess')

        # Return an object of this model
        return cls(component,
                   description,
                   gateway,
                   id,
                   ip,
                   netmask_bits,
                   netmask_ip_4,
                   nfs_access,
                   nfs_squash,
                   s_3_access,
                   smb_access)
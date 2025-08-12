# -*- coding: utf-8 -*-


class RemoteDisk(object):

    """Implementation of the 'Remote disk' model.

    Specifies the configuration of a remote disk.

    Attributes:
        id (long|int): Specifies the disk id.
        mount_path (string): Specifies the NFS mount path of the remote disk.
        node_id (long|int): Specifies the node id of the disk. If not
            specified, the disk will be evenly distributed across all the
            nodes.
        tier (TierEnum): Specifies the tier of the disk
        capacity_bytes (long|int): Specifies the capacity of the disk in
            bytes.
        used_capacity_bytes (long|int): Specifies the used capacity of remote
            disk in bytes.
        status (Status17Enum): Specifies the status of a remote disk.
        file_system_name (string): Specifies the name of filesystem on remote
            storage.
        data_vip (string): Specifies the data vip used to mount the
            filesystem.
        node_ip (string): Specifies ip address of the node that this remote
            disk is mounted on.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mount_path":'mountPath',
        "tier":'tier',
        "id":'id',
        "node_id":'nodeId',
        "capacity_bytes":'capacityBytes',
        "used_capacity_bytes":'usedCapacityBytes',
        "status":'status',
        "file_system_name":'fileSystemName',
        "data_vip":'dataVip',
        "node_ip":'nodeIp'
    }

    def __init__(self,
                 mount_path=None,
                 tier=None,
                 id=None,
                 node_id=None,
                 capacity_bytes=None,
                 used_capacity_bytes=None,
                 status=None,
                 file_system_name=None,
                 data_vip=None,
                 node_ip=None):
        """Constructor for the RemoteDisk class"""

        # Initialize members of the class
        self.id = id
        self.mount_path = mount_path
        self.node_id = node_id
        self.tier = tier
        self.capacity_bytes = capacity_bytes
        self.used_capacity_bytes = used_capacity_bytes
        self.status = status
        self.file_system_name = file_system_name
        self.data_vip = data_vip
        self.node_ip = node_ip


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
        mount_path = dictionary.get('mountPath')
        tier = dictionary.get('tier')
        id = dictionary.get('id')
        node_id = dictionary.get('nodeId')
        capacity_bytes = dictionary.get('capacityBytes')
        used_capacity_bytes = dictionary.get('usedCapacityBytes')
        status = dictionary.get('status')
        file_system_name = dictionary.get('fileSystemName')
        data_vip = dictionary.get('dataVip')
        node_ip = dictionary.get('nodeIp')

        # Return an object of this model
        return cls(mount_path,
                   tier,
                   id,
                   node_id,
                   capacity_bytes,
                   used_capacity_bytes,
                   status,
                   file_system_name,
                   data_vip,
                   node_ip)



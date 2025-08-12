# -*- coding: utf-8 -*-


class DiskDetails(object):

    """Implementation of the 'Disk details' model.

    Specifies the details of a disk that belongs to a node.

    Attributes:
        id (long|int): Specifies id to uniquely identify a disk.
        serial_number (string): Specifies serial number of disk.
        capacity_in_bytes (long|int): Specifies capacity of disk in bytes.
        model (string): Specifies product model of disk.
        node_id (long|int): Specifies node id of the node that this disk
            belong to.
        status (Status20Enum): Specifies status of the disk.
        mtype (Type22Enum): Specifies type of the disk.
        location (string): Specifies location of the disk in node.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "serial_number":'serialNumber',
        "capacity_in_bytes":'capacityInBytes',
        "model":'model',
        "node_id":'nodeId',
        "status":'status',
        "mtype":'type',
        "location":'location'
    }

    def __init__(self,
                 id=None,
                 serial_number=None,
                 capacity_in_bytes=None,
                 model=None,
                 node_id=None,
                 status=None,
                 mtype=None,
                 location=None):
        """Constructor for the DiskDetails class"""

        # Initialize members of the class
        self.id = id
        self.serial_number = serial_number
        self.capacity_in_bytes = capacity_in_bytes
        self.model = model
        self.node_id = node_id
        self.status = status
        self.mtype = mtype
        self.location = location


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
        serial_number = dictionary.get('serialNumber')
        capacity_in_bytes = dictionary.get('capacityInBytes')
        model = dictionary.get('model')
        node_id = dictionary.get('nodeId')
        status = dictionary.get('status')
        mtype = dictionary.get('type')
        location = dictionary.get('location')

        # Return an object of this model
        return cls(id,
                   serial_number,
                   capacity_in_bytes,
                   model,
                   node_id,
                   status,
                   mtype,
                   location)



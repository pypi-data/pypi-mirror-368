# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.free_disk

class NodeFreeDisks(object):

    """Implementation of the 'NodeFreeDisks' model.

    Sepcifies the free disks of a node.

    Attributes:
        node_id (long|int): Specifies the id of a node.
        free_disks (list of FreeDisk): Specifies list of free disks of node.
        chassis_serial (string): Chassis serial number.
        slot (long|int): Slot number of node
        error_message (string): Error message of disks assimilation request.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_id":'nodeId',
        "free_disks":'freeDisks',
        "chassis_serial":'chassisSerial',
        "slot":'slot',
        "error_message":'errorMessage'
    }

    def __init__(self,
                 node_id=None,
                 free_disks=None,
                 chassis_serial=None,
                 slot=None,
                 error_message=None):
        """Constructor for the NodeFreeDisks class"""

        # Initialize members of the class
        self.node_id = node_id
        self.free_disks = free_disks
        self.chassis_serial = chassis_serial
        self.slot = slot
        self.error_message = error_message


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
        node_id = dictionary.get('nodeId')
        free_disks = None
        if dictionary.get("freeDisks") is not None:
            free_disks = list()
            for structure in dictionary.get('freeDisks'):
                free_disks.append(cohesity_management_sdk.models_v2.free_disk.FreeDisk.from_dictionary(structure))
        chassis_serial = dictionary.get('chassisSerial')
        slot = dictionary.get('slot')
        error_message = dictionary.get('errorMessage')

        # Return an object of this model
        return cls(node_id,
                   free_disks,
                   chassis_serial,
                   slot,
                   error_message)



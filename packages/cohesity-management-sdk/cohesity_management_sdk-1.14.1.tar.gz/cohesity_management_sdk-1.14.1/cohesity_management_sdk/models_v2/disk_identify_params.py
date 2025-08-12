# -*- coding: utf-8 -*-


class DiskIdentifyParams(object):

    """Implementation of the 'Disk identify params.' model.

    Specifies the parameters needed to identify disk.

    Attributes:
        node_id (long|int): Specifies the node id of node that disk belongs
            to.
        serial_number (string): Specifies serial number of disk.
        identify (bool): Turn on/off led light if it is set to true/false

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_id":'nodeId',
        "serial_number":'serialNumber',
        "identify":'identify'
    }

    def __init__(self,
                 node_id=None,
                 serial_number=None,
                 identify=None):
        """Constructor for the DiskIdentifyParams class"""

        # Initialize members of the class
        self.node_id = node_id
        self.serial_number = serial_number
        self.identify = identify


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
        serial_number = dictionary.get('serialNumber')
        identify = dictionary.get('identify')

        # Return an object of this model
        return cls(node_id,
                   serial_number,
                   identify)



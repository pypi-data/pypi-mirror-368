# -*- coding: utf-8 -*-


class ChassisSpecificResponse(object):

    """Implementation of the 'Chassis specific response.' model.

    Specifies information about hardware chassis.

    Attributes:
        chassis_node_base (long|int): This field is initialized as sum of maximum slots of all the
          chassis added to the cluster so far plus one. This is required to assign
          unique node index for the nodes when they are added to the cluster. Please
          refer to cluster_node_index in Node below.
        id (long|int): Each chassis in a cluster is assigned a unique id when the chassis
          is added to the cluster first time. The index starts from 1. The use of
          an integer id helps speed up internal computations involving chassis. This
          integer will not change during the lifetime of the chassis in the cluster.
        hardware_model (string): Specifies the hardware model of the chassis.Like ivybridge, haswell.
        location (string): Location of the chassis within the rack.
        name (string): Unique name assigned to this chassis. This is set to the serial
          number of the chassis by one of the following two ways. 1) by the chassis
          manufacturer for non-cohesity systems, and cohesity systems built before
          jira ticket ECO-2 was approved. 2) by a cohesity contract manufacturer for
          cohesity systems built after jira ticket ECO-2 was approved.
        serial_number (string): Specifies the serial number of the chassis.
        node_ids (list of long|int): Specifies list of ids of all the nodes in
            chassis.
        rack_id (long|int): Rack Id that this chassis belong to

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "chassis_node_base":'chassisNodeBase',
        "id":'id',
        "hardware_model":'hardwareModel',
        "location":'location',
        "name":'name',
        "serial_number":'serialNumber',
        "node_ids":'nodeIds',
        "rack_id":'rackId'
    }

    def __init__(self,
                 chassis_node_base=None,
                 id=None,
                 hardware_model=None,
                 location=None,
                 name=None,
                 serial_number=None,
                 node_ids=None,
                 rack_id=None):
        """Constructor for the ChassisSpecificResponse class"""

        # Initialize members of the class
        self.chassis_node_base = chassis_node_base
        self.id = id
        self.hardware_model = hardware_model
        self.location = location
        self.name = name
        self.serial_number = serial_number
        self.node_ids = node_ids
        self.rack_id = rack_id


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
        chassis_node_base = dictionary.get('chassisNodeBase')
        id = dictionary.get('id')
        hardware_model = dictionary.get('hardwareModel')
        location = dictionary.get('location')
        name = dictionary.get('name')
        serial_number = dictionary.get('serialNumber')
        node_ids = dictionary.get('nodeIds')
        rack_id = dictionary.get('rackId')

        # Return an object of this model
        return cls(chassis_node_base,
                   id,
                   hardware_model,
                   location,
                   name,
                   serial_number,
                   node_ids,
                   rack_id)
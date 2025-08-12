# -*- coding: utf-8 -*-


class RackSpecificResponse(object):

    """Implementation of the 'Rack specific response.' model.

    Specifies information about rack.

    Attributes:
        id (long|int): Specifies unique id of the rack.
        name (string): Specifies name of the rack
        location (string): Specifies location of the rack.
        chassis_ids (list of long|int): List of chassis ids that are part of
            the rack.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "location":'location',
        "chassis_ids":'chassisIds'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 location=None,
                 chassis_ids=None):
        """Constructor for the RackSpecificResponse class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.location = location
        self.chassis_ids = chassis_ids


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
        name = dictionary.get('name')
        location = dictionary.get('location')
        chassis_ids = dictionary.get('chassisIds')

        # Return an object of this model
        return cls(id,
                   name,
                   location,
                   chassis_ids)



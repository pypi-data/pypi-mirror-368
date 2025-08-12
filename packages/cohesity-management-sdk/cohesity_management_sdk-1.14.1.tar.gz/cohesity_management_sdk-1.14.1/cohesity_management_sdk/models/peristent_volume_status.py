# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.peristent_volume_status_capacity_entry

class PeristentVolumeStatus(object):

    """Implementation of the 'PeristentVolumeStatus' model.

    IP Range for range of vip address addition.

    Attributes:
        capacity (list of PeristentVolumeStatus_CapacityEntry): capacity
            represents the actual resources of the underlying volume.
        phase (string): Describes the phase of PV i.e. whether it is bound or
            not.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "capacity": 'capacity',
        "phase": 'phase'
    }

    def __init__(self,
                 capacity=None,
                 phase=None):
        """Constructor for the PeristentVolumeStatus class"""

        # Initialize members of the class
        self.capacity = capacity
        self.phase = phase


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
        capacity = None
        if dictionary.get("capacity") is not None:
            capacity = list()
            for structure in dictionary.get('capacity'):
                capacity.append(cohesity_management_sdk.models.peristent_volume_status_capacity_entry.PeristentVolumeStatus_CapacityEntry.from_dictionary(structure))
        phase = dictionary.get('phase', None)

        # Return an object of this model
        return cls(capacity,
                   phase)



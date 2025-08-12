# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_snapshot

class ObjectSnapshots(object):

    """Implementation of the 'Object Snapshots.' model.

    Specifies the list of object snapshots.

    Attributes:
        snapshots (list of ObjectSnapshot): Specifies the list of snapshots.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshots":'snapshots'
    }

    def __init__(self,
                 snapshots=None):
        """Constructor for the ObjectSnapshots class"""

        # Initialize members of the class
        self.snapshots = snapshots


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
        snapshots = None
        if dictionary.get("snapshots") is not None:
            snapshots = list()
            for structure in dictionary.get('snapshots'):
                snapshots.append(cohesity_management_sdk.models_v2.object_snapshot.ObjectSnapshot.from_dictionary(structure))

        # Return an object of this model
        return cls(snapshots)



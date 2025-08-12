# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.indexed_object_snapshot

class GetIndexedObjectSnapshotsResponseBody(object):

    """Implementation of the 'GetIndexedObjectSnapshotsResponseBody' model.

    Specifies the snapshots of an indexed object.

    Attributes:
        snapshots (list of IndexedObjectSnapshot): Specifies a list of
            snapshots containing the indexed object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshots":'snapshots'
    }

    def __init__(self,
                 snapshots=None):
        """Constructor for the GetIndexedObjectSnapshotsResponseBody class"""

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
                snapshots.append(cohesity_management_sdk.models_v2.indexed_object_snapshot.IndexedObjectSnapshot.from_dictionary(structure))

        # Return an object of this model
        return cls(snapshots)



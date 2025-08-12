# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.snapshots_summary

class ObjectStats(object):

    """Implementation of the 'Object Stats.' model.

    Specifies the object stats.

    Attributes:
        snapshots_summary (list of SnapshotsSummary): Specifies a summary of
            the object snapshots.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshots_summary":'snapshotsSummary'
    }

    def __init__(self,
                 snapshots_summary=None):
        """Constructor for the ObjectStats class"""

        # Initialize members of the class
        self.snapshots_summary = snapshots_summary


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
        snapshots_summary = None
        if dictionary.get("snapshotsSummary") is not None:
            snapshots_summary = list()
            for structure in dictionary.get('snapshotsSummary'):
                snapshots_summary.append(cohesity_management_sdk.models_v2.snapshots_summary.SnapshotsSummary.from_dictionary(structure))

        # Return an object of this model
        return cls(snapshots_summary)



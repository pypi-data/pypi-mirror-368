# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.snapshot_folder_counts

class O365OutlookRestoreEntityParams(object):

    """Implementation of the 'O365OutlookRestoreEntityParams' model.

    This message defines the per object restore parameters for restoring a
      single user's mailbox.

    Attributes:

        snapshot_folder_counts (list of SnapshotFolderCounts): Stores the count of folders associated with different roots during the
          backup process in current snapshot.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_folder_counts":'snapshotFolderCounts'
    }

    def __init__(self,
                 snapshot_folder_counts=None
            ):

        """Constructor for the O365OutlookRestoreEntityParams class"""

        # Initialize members of the class
        self.snapshot_folder_counts = snapshot_folder_counts

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
        snapshot_folder_counts = None
        if dictionary.get('snapshotFolderCounts', None):
            snapshot_folder_counts = list()
            for structure in dictionary.get('snapshotFolderCounts'):
                snapshot_folder_counts.append(cohesity_management_sdk.models.snapshot_folder_counts.SnapshotFolderCounts.from_dictionary(structure))

        # Return an object of this model
        return cls(
            snapshot_folder_counts)
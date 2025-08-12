# -*- coding: utf-8 -*-


class SnapshotLabel(object):

    """Implementation of the 'Snapshot Label' model.

    Specifies the snapshot label for incremental and full backup of Secondary
    Netapp volumes (Data-Protect Volumes).

    Attributes:
        incremental_label (string): Specifies the incremental snapshot label
            value
        full_label (string): Specifies the full snapshot label value

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "incremental_label":'incrementalLabel',
        "full_label":'fullLabel'
    }

    def __init__(self,
                 incremental_label=None,
                 full_label=None):
        """Constructor for the SnapshotLabel class"""

        # Initialize members of the class
        self.incremental_label = incremental_label
        self.full_label = full_label


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
        incremental_label = dictionary.get('incrementalLabel')
        full_label = dictionary.get('fullLabel')

        # Return an object of this model
        return cls(incremental_label,
                   full_label)



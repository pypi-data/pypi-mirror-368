# -*- coding: utf-8 -*-


class ContinuousSnapshotParams(object):

    """Implementation of the 'Continuous Snapshot Params' model.

    Specifies the source snapshots to be taken even if there is a pending run
    in a protection group.

    Attributes:
        is_enabled (bool): Specifies whether source snapshots should be taken
            even if there is a pending run.
        max_allowed_snapshots (int): Specifies the maximum number of source
            snapshots allowed for a given object in a protection group. This
            is only applicable if isContinuousSnapshottingEnabled is set to
            true.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_enabled":'isEnabled',
        "max_allowed_snapshots":'maxAllowedSnapshots'
    }

    def __init__(self,
                 is_enabled=None,
                 max_allowed_snapshots=None):
        """Constructor for the ContinuousSnapshotParams class"""

        # Initialize members of the class
        self.is_enabled = is_enabled
        self.max_allowed_snapshots = max_allowed_snapshots


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
        is_enabled = dictionary.get('isEnabled')
        max_allowed_snapshots = dictionary.get('maxAllowedSnapshots')

        # Return an object of this model
        return cls(is_enabled,
                   max_allowed_snapshots)



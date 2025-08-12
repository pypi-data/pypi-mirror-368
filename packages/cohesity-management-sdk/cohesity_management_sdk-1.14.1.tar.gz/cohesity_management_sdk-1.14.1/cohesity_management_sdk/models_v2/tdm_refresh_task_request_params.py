# -*- coding: utf-8 -*-


class TdmRefreshTaskRequestParams(object):

    """Implementation of the 'TdmRefreshTaskRequestParams' model.

    Specifies the parameters to refresh a clone with new data.

    Attributes:
        clone_id (string): Specifies the ID of the clone, which needs to be
            refreshed.
        snapshot_id (string): Specifies the snapshot ID, using which the clone
            is to be refreshed.
        description (string): Specifies the description of the clone refresh
            task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "clone_id":'cloneId',
        "snapshot_id":'snapshotId',
        "description":'description'
    }

    def __init__(self,
                 clone_id=None,
                 snapshot_id=None,
                 description=None):
        """Constructor for the TdmRefreshTaskRequestParams class"""

        # Initialize members of the class
        self.clone_id = clone_id
        self.snapshot_id = snapshot_id
        self.description = description


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
        clone_id = dictionary.get('cloneId')
        snapshot_id = dictionary.get('snapshotId')
        description = dictionary.get('description')

        # Return an object of this model
        return cls(clone_id,
                   snapshot_id,
                   description)



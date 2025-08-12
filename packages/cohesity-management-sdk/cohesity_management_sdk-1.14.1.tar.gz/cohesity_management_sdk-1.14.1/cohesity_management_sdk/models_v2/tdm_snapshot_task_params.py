# -*- coding: utf-8 -*-


class TdmSnapshotTaskParams(object):

    """Implementation of the 'TdmSnapshotTaskParams' model.

    Specifies the parameters to create a snapshot of an existing clone.

    Attributes:
        clone_id (string): Specifies the ID of the clone.
        label (string): Specifies the label for the snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "clone_id":'cloneId',
        "label":'label'
    }

    def __init__(self,
                 clone_id=None,
                 label=None):
        """Constructor for the TdmSnapshotTaskParams class"""

        # Initialize members of the class
        self.clone_id = clone_id
        self.label = label


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
        label = dictionary.get('label')

        # Return an object of this model
        return cls(clone_id,
                   label)



# -*- coding: utf-8 -*-


class CommonTdmCloneSnapshotParams(object):

    """Implementation of the 'CommonTdmCloneSnapshotParams' model.

    Specifies the common properties of a clone snapshot.

    Attributes:
        label (string): Specifies the label for the snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "label":'label'
    }

    def __init__(self,
                 label=None):
        """Constructor for the CommonTdmCloneSnapshotParams class"""

        # Initialize members of the class
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
        label = dictionary.get('label')

        # Return an object of this model
        return cls(label)



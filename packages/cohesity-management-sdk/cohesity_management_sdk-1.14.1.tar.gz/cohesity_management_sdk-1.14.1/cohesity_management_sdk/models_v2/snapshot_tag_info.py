# -*- coding: utf-8 -*-


class SnapshotTagInfo(object):

    """Implementation of the 'SnapshotTagInfo' model.

    Specifies the snapshot tag info for an object.

    Attributes:
        tag_id (string): Specifies Id of tag applied to the object.
        run_ids (list of string): Specifies runs the tags are applied to.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tag_id":'tagId',
        "run_ids":'runIds'
    }

    def __init__(self,
                 tag_id=None,
                 run_ids=None):
        """Constructor for the SnapshotTagInfo class"""

        # Initialize members of the class
        self.tag_id = tag_id
        self.run_ids = run_ids


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
        tag_id = dictionary.get('tagId')
        run_ids = dictionary.get('runIds')

        # Return an object of this model
        return cls(tag_id,
                   run_ids)



# -*- coding: utf-8 -*-


class TagInfo(object):

    """Implementation of the 'TagInfo' model.

    Specifies the tag info for an object.

    Attributes:
        tag_id (string): Specifies Id of tag applied to the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tag_id":'tagId'
    }

    def __init__(self,
                 tag_id=None):
        """Constructor for the TagInfo class"""

        # Initialize members of the class
        self.tag_id = tag_id


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

        # Return an object of this model
        return cls(tag_id)



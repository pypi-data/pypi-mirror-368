# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tag_info
import cohesity_management_sdk.models_v2.snapshot_tag_info

class TagObject(object):

    """Implementation of the 'TagObject' model.

    Specifies all the tag related info for an object.

    Attributes:
        tags (list of TagInfo): Specifies tag applied to the object.
        snapshot_tags (list of SnapshotTagInfo): Specifies snapshot tags
            applied to the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tags":'tags',
        "snapshot_tags":'snapshotTags'
    }

    def __init__(self,
                 tags=None,
                 snapshot_tags=None):
        """Constructor for the TagObject class"""

        # Initialize members of the class
        self.tags = tags
        self.snapshot_tags = snapshot_tags


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
        tags = None
        if dictionary.get("tags") is not None:
            tags = list()
            for structure in dictionary.get('tags'):
                tags.append(cohesity_management_sdk.models_v2.tag_info.TagInfo.from_dictionary(structure))
        snapshot_tags = None
        if dictionary.get("snapshotTags") is not None:
            snapshot_tags = list()
            for structure in dictionary.get('snapshotTags'):
                snapshot_tags.append(cohesity_management_sdk.models_v2.snapshot_tag_info.SnapshotTagInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(tags,
                   snapshot_tags)



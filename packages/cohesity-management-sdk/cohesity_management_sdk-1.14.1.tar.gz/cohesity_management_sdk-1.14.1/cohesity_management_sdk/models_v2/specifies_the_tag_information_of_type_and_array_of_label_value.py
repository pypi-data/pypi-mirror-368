# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.specifies_label_and_value_of_tags

class SpecifiesTheTagInformationOfTypeAndArrayOfLabelValue(object):

    """Implementation of the 'Specifies the tag information of type and array of (label, value).' model.

    TODO: type model description here.

    Attributes:
        mtype (string): Specifies type of tag.
        tags (list of SpecifiesLabelAndValueOfTags): Array of tag label and
            value.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "tags":'tags'
    }

    def __init__(self,
                 mtype=None,
                 tags=None):
        """Constructor for the SpecifiesTheTagInformationOfTypeAndArrayOfLabelValue class"""

        # Initialize members of the class
        self.mtype = mtype
        self.tags = tags


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
        mtype = dictionary.get('type')
        tags = None
        if dictionary.get("tags") is not None:
            tags = list()
            for structure in dictionary.get('tags'):
                tags.append(cohesity_management_sdk.models_v2.specifies_label_and_value_of_tags.SpecifiesLabelAndValueOfTags.from_dictionary(structure))

        # Return an object of this model
        return cls(mtype,
                   tags)



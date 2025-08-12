# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.specifies_the_tag_information_of_type_and_array_of_label_value

class DataTieringTagConfig(object):

    """Implementation of the 'DataTieringTagConfig' model.

    Array of data tiering tag objects.

    Attributes:
        id (string): Specifies the ID of the data tiering analysis group.
        tags_info (list of
            SpecifiesTheTagInformationOfTypeAndArrayOfLabelValue): Array of
            Tag objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tags_info":'tagsInfo',
        "id":'id'
    }

    def __init__(self,
                 tags_info=None,
                 id=None):
        """Constructor for the DataTieringTagConfig class"""

        # Initialize members of the class
        self.id = id
        self.tags_info = tags_info


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
        tags_info = None
        if dictionary.get("tagsInfo") is not None:
            tags_info = list()
            for structure in dictionary.get('tagsInfo'):
                tags_info.append(cohesity_management_sdk.models_v2.specifies_the_tag_information_of_type_and_array_of_label_value.SpecifiesTheTagInformationOfTypeAndArrayOfLabelValue.from_dictionary(structure))
        id = dictionary.get('id')

        # Return an object of this model
        return cls(tags_info,
                   id)



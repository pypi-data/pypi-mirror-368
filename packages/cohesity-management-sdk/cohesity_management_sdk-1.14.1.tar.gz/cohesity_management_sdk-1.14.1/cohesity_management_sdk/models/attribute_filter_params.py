# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


class AttributeFilterParams(object):

    """Implementation of the 'AttributeFilterParams' model.

    Specifies the filter parameters which can be used to provide exclusions
    OR inclusions of entities based on attributes within entity proto within
    backup jobs.
    Currently this is only used by O365 adapter but can be used by others as
    well to introduce attribute based filtering by adding corresponding
    ''AttributeType''.
    eg: For providing a matching criteria on all kUser entities belonging to
    the department - ''Engineering'', following should be the message:
    {
    attr_key: kDepartment
    attr_value_vec: ''Engineering''
    }'

    Attributes:
        attr_key (int): Specifies the attribute key whose values are to be
            matched for entity inclusions/exclusions.
        attr_value_vec (list of string): Specifies the list of attribute values
            against which entity attribute values are to be matched against.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "attr_key": 'attrKey',
        "attr_value_vec": 'attrValueVec'
    }

    def __init__(self,
                 attr_key=None,
                 attr_value_vec=None):
        """Constructor for the AttributeFilterParams class"""

        # Initialize members of the class
        self.attr_key = attr_key
        self.attr_value_vec = attr_value_vec


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
        attr_key = dictionary.get('attrKey', None)
        attr_value_vec = dictionary.get('attrValueVec', None)

        # Return an object of this model
        return cls(attr_key,
                   attr_value_vec)



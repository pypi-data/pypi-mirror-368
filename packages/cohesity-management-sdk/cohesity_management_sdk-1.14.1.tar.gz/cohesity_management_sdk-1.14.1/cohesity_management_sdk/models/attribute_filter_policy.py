# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.


import cohesity_management_sdk.models.attribute_filter_params

class AttributeFilterPolicy(object):

    """Implementation of the 'AttributeFilterPolicy' model.

    Specifies the filter policy which can be applied on the entities being
	backed up within a job. The filter policy supports both inclusions &
	exclusions. In scenarios where, there is an overlap between inclusions
	and exclusions, it the adapter''s responsibility to choose the precedence.
	Currently this is only used by O365 within Mailbox & OneDrive backup params.
	Precedence is given to inclusion.
	Eg: To create an inclusion filter within a job for autoprotection on
	department as ''Engineering'' & display_name starting with [A, B, C], below
	is the param:
	inclusion_attr_params: {
	attr_key: kDepartment
	attr_value_vec: "Engineering"
	}
	inclusion_attr_params: {
	attr_key: kDisplayNamePrefixAlphabet
	attr_value_vec: "A"
	attr_value_vec: "B"
	attr_value_vec: "C"
	}

    Attributes:
        exclusion_attr_params (list of AttributeFilterParams): Specifies the
            exclusion attributes.
        inclusion_attr_params (list of AttributeFilterParams): Specifies the
            inclusion attributes.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclusion_attr_params": 'exclusionAttrParams',
        "inclusion_attr_params": 'inclusionAttrParams'
    }

    def __init__(self,
                 exclusion_attr_params=None,
                 inclusion_attr_params=None):
        """Constructor for the AttributeFilterPolicy class"""

        # Initialize members of the class
        self.exclusion_attr_params = exclusion_attr_params
        self.inclusion_attr_params = inclusion_attr_params


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
        exclusion_attr_params = None
        if dictionary.get("exclusionAttrParams", None) is not None:
            exclusion_attr_params = list()
            for structure in dictionary.get('exclusionAttrParams'):
                exclusion_attr_params.append(cohesity_management_sdk.models.attribute_filter_params.AttributeFilterParams.from_dictionary(structure))
        inclusion_attr_params = None
        if dictionary.get("inclusionAttrParams", None) is not None:
            inclusion_attr_params = list()
            for structure in dictionary.get('inclusionAttrParams'):
                inclusion_attr_params.append(cohesity_management_sdk.models.attribute_filter_params.AttributeFilterParams.from_dictionary(structure))

        # Return an object of this model
        return cls(exclusion_attr_params,
                   inclusion_attr_params)



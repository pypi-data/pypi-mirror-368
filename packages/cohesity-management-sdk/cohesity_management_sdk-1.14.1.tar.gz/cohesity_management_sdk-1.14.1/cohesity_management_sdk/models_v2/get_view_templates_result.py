# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.template

class GetViewTemplatesResult(object):

    """Implementation of the 'Get view templates Result.' model.

    Specifies the list of view template returned that matched the specified
    filter
    criteria.

    Attributes:
        templates (list of Template): Array of view template. Specifies the
            list of view templates returned in this response.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "templates":'Templates'
    }

    def __init__(self,
                 templates=None):
        """Constructor for the GetViewTemplatesResult class"""

        # Initialize members of the class
        self.templates = templates


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
        templates = None
        if dictionary.get("Templates") is not None:
            templates = list()
            for structure in dictionary.get('Templates'):
                templates.append(cohesity_management_sdk.models_v2.template.Template.from_dictionary(structure))

        # Return an object of this model
        return cls(templates)



# -*- coding: utf-8 -*-


class ViewIntent(object):

    """Implementation of the 'ViewIntent' model.

    Sepcifies the intent of the View.

    Attributes:
        default_template_name (DefaultTemplateNameEnum): Used for uniquely indentifying a default template
        template_id (long|int64): Specifies the template id from which the View is created.
        template_name (string): Specifies the template name from which the View is created.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "default_template_name":'defaultTemplateName',
        "template_id":'templateId',
        "template_name":'templateName'
    }

    def __init__(self,
                 default_template_name=None,
                 template_id=None,
                 template_name=None):
        """Constructor for the ViewIntent class"""

        # Initialize members of the class
        self.default_template_name = default_template_name
        self.template_id = template_id
        self.template_name = template_name


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
        default_template_name = dictionary.get('defaultTemplateName')
        template_id = dictionary.get('templateId')
        template_name = dictionary.get('templateName')

        # Return an object of this model
        return cls(default_template_name,
                   template_id,
                   template_name)
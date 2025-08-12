# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.view_1

class Template(object):

    """Implementation of the 'Template.' model.

    Description of the view template.

    Attributes:
        id (long|int): Specifies an id of the view template.
        name (string): Specifies the name of the view template.
        dedup (bool): Specifies whether to enable dedup in storage domain.
        compress (bool): Specifies whether to enable compression in storage
            domain.
        is_default (bool): Specifies if the tempate is custom or static.
        view_category (ViewCategoryEnum): Deprecated. Use category defined in
            viewParams instead.
        default_template_name (DefaultTemplateNameEnum): Used for uniquely
            indentifying a default template.
        principal_id (long|int): Deprecated. Use principalId defined in
            viewParams.qos instead.
        view_params (View1): Specifies settings for defining a storage
            location (called a View) with NFS and SMB mount paths in a Storage
            Domain (View Box) on the Cohesity Cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "dedup":'dedup',
        "compress":'compress',
        "is_default":'isDefault',
        "view_category":'viewCategory',
        "default_template_name":'defaultTemplateName',
        "principal_id":'principalId',
        "view_params":'viewParams'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 dedup=None,
                 compress=None,
                 is_default=None,
                 view_category=None,
                 default_template_name=None,
                 principal_id=None,
                 view_params=None):
        """Constructor for the Template class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.dedup = dedup
        self.compress = compress
        self.is_default = is_default
        self.view_category = view_category
        self.default_template_name = default_template_name
        self.principal_id = principal_id
        self.view_params = view_params


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        dedup = dictionary.get('dedup')
        compress = dictionary.get('compress')
        is_default = dictionary.get('isDefault')
        view_category = dictionary.get('viewCategory')
        default_template_name = dictionary.get('defaultTemplateName')
        principal_id = dictionary.get('principalId')
        view_params = cohesity_management_sdk.models_v2.view_1.View1.from_dictionary(dictionary.get('viewParams')) if dictionary.get('viewParams') else None

        # Return an object of this model
        return cls(id,
                   name,
                   dedup,
                   compress,
                   is_default,
                   view_category,
                   default_template_name,
                   principal_id,
                   view_params)



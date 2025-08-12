# -*- coding: utf-8 -*-


class BaseCreateViewRequest(object):

    """Implementation of the 'Base Create View Request.' model.

    Specifies the base information required for creating a new View.

    Attributes:
        name (string): Specifies the name of the new View to create.
        category (Category1Enum): Specifies the category of the View.
        storage_domain_id (long|int): Specifies the id of the Storage Domain
            (View Box) where the View will be created.
        case_insensitive_names_enabled (bool): Specifies whether to support
            case insensitive file/folder names. This parameter can only be set
            during create and cannot be changed.
        object_services_mapping_config (ObjectServicesMappingConfigEnum):
            Specifies the Object Services key mapping config of the view. This
            parameter can only be set during create and cannot be changed.
            Configuration of Object Services key mapping. Specifies the type
            of Object Services key mapping config.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "category":'category',
        "storage_domain_id":'storageDomainId',
        "case_insensitive_names_enabled":'caseInsensitiveNamesEnabled',
        "object_services_mapping_config":'objectServicesMappingConfig'
    }

    def __init__(self,
                 name=None,
                 category=None,
                 storage_domain_id=None,
                 case_insensitive_names_enabled=None,
                 object_services_mapping_config=None):
        """Constructor for the BaseCreateViewRequest class"""

        # Initialize members of the class
        self.name = name
        self.category = category
        self.storage_domain_id = storage_domain_id
        self.case_insensitive_names_enabled = case_insensitive_names_enabled
        self.object_services_mapping_config = object_services_mapping_config


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
        name = dictionary.get('name')
        category = dictionary.get('category')
        storage_domain_id = dictionary.get('storageDomainId')
        case_insensitive_names_enabled = dictionary.get('caseInsensitiveNamesEnabled')
        object_services_mapping_config = dictionary.get('objectServicesMappingConfig')

        # Return an object of this model
        return cls(name,
                   category,
                   storage_domain_id,
                   case_insensitive_names_enabled,
                   object_services_mapping_config)



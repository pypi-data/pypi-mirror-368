# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.fallback_option

class AdCentrifyTypeParams(object):

    """Implementation of the 'AdCentrifyTypeParams' model.

    Specifies the properties associated to a Centrify type user id mapping.

    Attributes:
        description (string): Specifies a description of the Centrify zone.
        distinguished_name (string): Specifies the distinguished name of the
            Centrify zone.
        schema (SchemaEnum): Specifies the schema of this Centrify zone.
        zone_name (string): Specifies the zone name of the Centrify zone.
        zone_domain (string): Specifies the zone domain of the Centrify zone.
        fallback_option (FallbackOption): Specifies a fallback user id mapping
            param in case the primary config does not work.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "description":'description',
        "distinguished_name":'distinguishedName',
        "schema":'schema',
        "fallback_option":'fallbackOption',
        "zone_name":'zoneName',
        "zone_domain":'zoneDomain'
    }

    def __init__(self,
                 description=None,
                 distinguished_name=None,
                 schema=None,
                 fallback_option=None,
                 zone_name=None,
                 zone_domain=None):
        """Constructor for the AdCentrifyTypeParams class"""

        # Initialize members of the class
        self.description = description
        self.distinguished_name = distinguished_name
        self.schema = schema
        self.zone_name = zone_name
        self.zone_domain = zone_domain
        self.fallback_option = fallback_option


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
        description = dictionary.get('description')
        distinguished_name = dictionary.get('distinguishedName')
        schema = dictionary.get('schema')
        fallback_option = cohesity_management_sdk.models_v2.fallback_option.FallbackOption.from_dictionary(dictionary.get('fallbackOption')) if dictionary.get('fallbackOption') else None
        zone_name = dictionary.get('zoneName')
        zone_domain = dictionary.get('zoneDomain')

        # Return an object of this model
        return cls(description,
                   distinguished_name,
                   schema,
                   fallback_option,
                   zone_name,
                   zone_domain)



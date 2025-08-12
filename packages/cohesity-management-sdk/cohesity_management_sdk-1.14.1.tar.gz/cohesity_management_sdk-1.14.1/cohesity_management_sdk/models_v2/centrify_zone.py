# -*- coding: utf-8 -*-


class CentrifyZone(object):

    """Implementation of the 'CentrifyZone' model.

    Specifies a centrify zone.

    Attributes:
        description (string): Specifies a description of the Centrify zone.
        distinguished_name (string): Specifies the distinguished name of the
            Centrify zone.
        schema (SchemaEnum): Specifies the schema of this Centrify zone.
        zone_name (string): Specifies the zone name of the Centrify zone.
        zone_domain (string): Specifies the zone domain of the Centrify zone.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "description":'description',
        "distinguished_name":'distinguishedName',
        "schema":'schema',
        "zone_name":'zoneName',
        "zone_domain":'zoneDomain'
    }

    def __init__(self,
                 description=None,
                 distinguished_name=None,
                 schema=None,
                 zone_name=None,
                 zone_domain=None):
        """Constructor for the CentrifyZone class"""

        # Initialize members of the class
        self.description = description
        self.distinguished_name = distinguished_name
        self.schema = schema
        self.zone_name = zone_name
        self.zone_domain = zone_domain


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
        zone_name = dictionary.get('zoneName')
        zone_domain = dictionary.get('zoneDomain')

        # Return an object of this model
        return cls(description,
                   distinguished_name,
                   schema,
                   zone_name,
                   zone_domain)



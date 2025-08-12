# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.object_string_identifier

class ObjectIdentifier(object):

    """Implementation of the 'Object Identifier.' model.

    Specifies the basic info to identify an object.

    Attributes:
        entity_id (ObjectStringIdentifier): Specifies the string based Id for an object and also provides
          the history of ids assigned to the object
        environment (EnvironmentEnum): Specifies the environment of the
            object.
        id (long|int64): Specifies object id.
        name (string): Specifies the name of the object.
        source_id (long|int): Specifies registered source id to which object
            belongs.
        source_name (string): Specifies registered source name to which object
            belongs.


    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_id":'entityId',
        "environment":'environment',
        "id":'id',
        "name":'name',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 entity_id=None,
                 environment=None,
                 id=None,
                 name=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the ObjectIdentifier class"""

        # Initialize members of the class
        self.entity_id = entity_id
        self.environment = environment
        self.id = id
        self.name = name
        self.source_id = source_id
        self.source_name = source_name


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
        entity_id = cohesity_management_sdk.models_v2.object_string_identifier.ObjectStringIdentifier.from_dictionary(dictionary.get('entityId')) if dictionary.get('entityId') else None
        environment = dictionary.get('environment')
        id = dictionary.get('id')
        name = dictionary.get('name')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(
                   entity_id,
                   environment,
                   id,
                   name,
                   source_id,
                   source_name)
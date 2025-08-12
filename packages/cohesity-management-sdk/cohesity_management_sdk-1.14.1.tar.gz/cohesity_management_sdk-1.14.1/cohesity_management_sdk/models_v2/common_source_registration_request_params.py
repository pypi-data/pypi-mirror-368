# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_information
import cohesity_management_sdk.models_v2.key_value_pair

class CommonSourceRegistrationRequestParams(object):

    """Implementation of the 'CommonSourceRegistrationRequestParams' model.

    Specifies the parameters which are common between all Protection Source
    registrations.

    Attributes:
        id (long|int): Source Registration ID. This can be used to retrieve,
            edit or delete the source registration.
        source_id (long|int): ID of top level source object discovered after
            the registration.
        source_info (ObjectInformation): Specifies detailed info about the source.
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.
        advanced_configs (list of KeyValuePair): Specifies the advanced configuration
            for a protection source.
        connection_id (long|int): Specifies the id of the connection from where this source is
            reachable. This should only be set for a source being registered by a
            tenant user. This field will be depricated in future. Use connections
            field.
        encryption_key (string): Specifies the key that user has encrypted the credential with.
        is_internal_encrypted (bool): Specifies if credentials are encrypted by internal key.
        connections (list of ConnectionConfig): Specfies the list of connections for the source.
        connector_group_id (long|int): Specifies the connector group id of connector groups.
        name (string): A user specified name for this source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "source_id":'sourceId',
        "source_info":'sourceInfo',
        "environment":'environment',
        "advanced_configs":'advancedConfigs',
        "connection_id":'connectionId',
        "encryption_key":'encryptionKey',
        "is_internal_encrypted":'isInternalEncrypted',
        "connections":'connections',
        "connector_group_id":'connectorGroupId',
        "name":'name'
    }

    def __init__(self,
                 id=None ,
                 source_id=None ,
                 source_info=None ,
                 environment=None ,
                 advanced_configs=None ,
                 connection_id=None ,
                 encryption_key=None ,
                 is_internal_encrypted=None ,
                 connections=None ,
                 connector_group_id=None ,
                 name=None):
        """Constructor for the CommonSourceRegistrationRequestParams class"""

        # Initialize members of the class
        self.id = id
        self.source_id = source_id
        self.source_info = source_info
        self.environment = environment
        self.advanced_configs = advanced_configs
        self.connection_id = connection_id
        self.encryption_key = encryption_key
        self.is_internal_encrypted = is_internal_encrypted
        self.connections = connections
        self.connector_group_id = connector_group_id
        self.environment = environment
        self.name = name


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
        source_id = dictionary.get('sourceId')
        source_info = cohesity_management_sdk.models_v2.object_information.Object.from_dictionary(
            dictionary.get('sourceInfo'))
        environment = dictionary.get('environment')
        advanced_configs = None
        if dictionary.get('advancedConfigs') is not None :
            advanced_configs = list()
            for structure in dictionary.get('advancedConfigs') :
                advanced_configs.append(
                    cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        connection_id = dictionary.get('connectionId')
        encryption_key = dictionary.get('encryptionKey')
        is_internal_encrypted = dictionary.get('isInternalEncrypted')
        connections = dictionary.get('connections')
        connector_group_id = dictionary.get('connectorGroupId')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(id,
                   source_id,
                   source_info,
                   environment,
                   advanced_configs,
                   connection_id,
                   encryption_key,
                   is_internal_encrypted,
                   connections,
                   connector_group_id,
                   name)
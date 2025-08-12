# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.hadoop_discovery_params

class HiveConnectParams(object):

    """Implementation of the 'HiveConnectParams' model.

    Specifies an Object containing information about a registered Hive
    source.

    Attributes:
        hdfs_entity_id (int|long): Specifies the entity id of the HDFS source
            for this Hive
        hive_discovery_params(HadoopDiscoveryParams): Specifies the Hive
            discovery params.
        kerberos_principal (string): Specifies the kerberos principal.
        metastore (string): Specifies the Hive metastore host.
        thrift_port (int): Specifies the Hive metastore thrift Port

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hdfs_entity_id":'hdfsEntityId',
        "hive_discovery_params": 'hiveDiscoveryParams',
        "kerberos_principal":'kerberosPrincipal',
        "metastore": 'metastore',
        "thrift_port": 'thriftPort'
    }

    def __init__(self,
                 hdfs_entity_id=None,
                 hive_discovery_params=None,
                 kerberos_principal=None,
                 metastore=None,
                 thrift_port=None):
        """Constructor for the HiveConnectParams class"""

        # Initialize members of the class
        self.hdfs_entity_id = hdfs_entity_id
        self.hive_discovery_params = hive_discovery_params
        self.kerberos_principal = kerberos_principal
        self.metastore = metastore
        self.thrift_port = thrift_port


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
        hdfs_entity_id = dictionary.get('hdfsEntityId')
        hive_discovery_params= cohesity_management_sdk.models.hadoop_discovery_params.HadoopDiscoveryParams.from_dictionary(dictionary.get('hiveDiscoveryParams')) if dictionary.get('hiveDiscoveryParams') else None
        kerberos_principal = dictionary.get('kerberosPrincipal')
        metastore = dictionary.get('metastore', None)
        thrift_port = dictionary.get('thriftPort', None)

        # Return an object of this model
        return cls(hdfs_entity_id,
                   hive_discovery_params,
                   kerberos_principal,
                   metastore,
                   thrift_port)



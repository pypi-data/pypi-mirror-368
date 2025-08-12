# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.hadoop_discovery_params

class HBaseConnectParams(object):

    """Implementation of the 'HBaseConnectParams' model.

    Specifies an Object containing information about a registered HBase
    source.

    Attributes:
        hbase_discovery_params (HadoopDiscoveryParams): Specifies the HBase
            discovery params.
        hdfs_entity_id long|int): The entity id of the HDFS source for this
            HBase
        kerberos_principal (string): Specifies the kerberos principal
        root_data_directory (string): Specifies the HBase data root directory.
        zookeeper_quorum (list of string): Specifies the HBase zookeeper
            quorum.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "hbase_discovery_params": 'hbaseDiscoveryParams',
        "hdfs_entity_id":'hdfsEntityId',
        "kerberos_principal":'kerberosPrincipal',
        "root_data_directory":'rootDataDirectory',
        "zookeeper_quorum":'zookeeperQuorum'
    }

    def __init__(self,
                 hbase_discovery_params=None,
                 hdfs_entity_id=None,
                 kerberos_principal=None,
                 root_data_directory=None,
                 zookeeper_quorum=None):
        """Constructor for the HBaseConnectParams class"""

        # Initialize members of the class
        self.hbase_discovery_params = hbase_discovery_params
        self.hdfs_entity_id = hdfs_entity_id
        self.kerberos_principal = kerberos_principal
        self.root_data_directory = root_data_directory
        self.zookeeper_quorum = zookeeper_quorum


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
        hbase_discovery_params = cohesity_management_sdk.models.hadoop_discovery_params.HadoopDiscoveryParams.from_dictionary(dictionary.get('hbaseDiscoveryParams')) if dictionary.get('hbaseDiscoveryParams') else None
        hdfs_entity_id = dictionary.get('hdfsEntityId')
        kerberos_principal = dictionary.get('kerberosPrincipal')
        root_data_directory = dictionary.get('rootDataDirectory')
        zookeeper_quorum = dictionary.get('zookeeperQuorum')

        # Return an object of this model
        return cls(hbase_discovery_params,
                   hdfs_entity_id,
                   kerberos_principal,
                   root_data_directory,
                   zookeeper_quorum)



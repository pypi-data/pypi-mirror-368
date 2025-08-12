# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_target_configuration
import cohesity_management_sdk.models_v2.azure_target_configuration

class ReplicationTarget(object):

    """Implementation of the 'Replication target.' model.

    Specifies replication target summary information.

    Attributes:
        cluster_id (long|int): Specifies the id of the cluster.
        cluster_incarnation_id (long|int): Specifies the incarnation id of the
            cluster.
        cluster_name (string): Specifies the name of the cluster.
        aws_target_config (AWSTargetConfiguration): Specifies the
            configuration for adding AWS as repilcation target
        azure_target_config (AzureTargetConfiguration): Specifies the
            configuration for adding Azure as replication target

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cluster_id":'clusterId',
        "cluster_incarnation_id":'clusterIncarnationId',
        "cluster_name":'clusterName',
        "aws_target_config":'awsTargetConfig',
        "azure_target_config":'azureTargetConfig'
    }

    def __init__(self,
                 cluster_id=None,
                 cluster_incarnation_id=None,
                 cluster_name=None,
                 aws_target_config=None,
                 azure_target_config=None):
        """Constructor for the ReplicationTarget class"""

        # Initialize members of the class
        self.cluster_id = cluster_id
        self.cluster_incarnation_id = cluster_incarnation_id
        self.cluster_name = cluster_name
        self.aws_target_config = aws_target_config
        self.azure_target_config = azure_target_config


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
        cluster_id = dictionary.get('clusterId')
        cluster_incarnation_id = dictionary.get('clusterIncarnationId')
        cluster_name = dictionary.get('clusterName')
        aws_target_config = cohesity_management_sdk.models_v2.aws_target_configuration.AWSTargetConfiguration.from_dictionary(dictionary.get('awsTargetConfig')) if dictionary.get('awsTargetConfig') else None
        azure_target_config = cohesity_management_sdk.models_v2.azure_target_configuration.AzureTargetConfiguration.from_dictionary(dictionary.get('azureTargetConfig')) if dictionary.get('azureTargetConfig') else None

        # Return an object of this model
        return cls(cluster_id,
                   cluster_incarnation_id,
                   cluster_name,
                   aws_target_config,
                   azure_target_config)



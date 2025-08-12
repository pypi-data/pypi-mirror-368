# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.schedule
import cohesity_management_sdk.models_v2.retention
import cohesity_management_sdk.models_v2.cluster_target_configuration
import cohesity_management_sdk.models_v2.aws_target_configuration
import cohesity_management_sdk.models_v2.azure_target_configuration

class ReplicationTargetConfiguration2(object):

    """Implementation of the 'Replication Target Configuration2' model.

    Specifies settings for copying Snapshots to Remote Clusters. This also
    specifies the retention policy that should be applied to Snapshots after
    they have been copied to the specified target.

    Attributes:
        schedule (Schedule): Specifies a schedule frequency and schedule unit
            for copying Snapshots to backup targets.
        retention (Retention): Specifies the retention of a backup.
        copy_on_run_success (bool): Specifies if Snapshots are copied from the
            first completely successful Protection Group Run or the first
            partially successful Protection Group Run occurring at the start
            of the replication schedule. <br> If true, Snapshots are copied
            from the first Protection Group Run occurring at the start of the
            replication schedule that was completely successful i.e. Snapshots
            for all the Objects in the Protection Group were successfully
            captured. <br> If false, Snapshots are copied from the first
            Protection Group Run occurring at the start of the replication
            schedule, even if first Protection Group Run was not completely
            successful i.e. Snapshots were not captured for all Objects in the
            Protection Group.
        config_id (string): Specifies the unique identifier for the target
            getting added. This field need to be passed only when policies are
            being updated.
        target_type (TargetType3Enum): Specifies the type of target to which
            replication need to be performed.
        remote_target_config (ClusterTargetConfiguration): Specifies the
            configuration for adding remote cluster as repilcation target
        aws_target_config (AWSTargetConfiguration): Specifies the
            configuration for adding AWS as repilcation target
        azure_target_config (AzureTargetConfiguration): Specifies the
            configuration for adding Azure as replication target

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "schedule":'schedule',
        "retention":'retention',
        "target_type":'targetType',
        "copy_on_run_success":'copyOnRunSuccess',
        "config_id":'configId',
        "remote_target_config":'remoteTargetConfig',
        "aws_target_config":'awsTargetConfig',
        "azure_target_config":'azureTargetConfig'
    }

    def __init__(self,
                 schedule=None,
                 retention=None,
                 target_type=None,
                 copy_on_run_success=None,
                 config_id=None,
                 remote_target_config=None,
                 aws_target_config=None,
                 azure_target_config=None):
        """Constructor for the ReplicationTargetConfiguration2 class"""

        # Initialize members of the class
        self.schedule = schedule
        self.retention = retention
        self.copy_on_run_success = copy_on_run_success
        self.config_id = config_id
        self.target_type = target_type
        self.remote_target_config = remote_target_config
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
        schedule = cohesity_management_sdk.models_v2.schedule.Schedule.from_dictionary(dictionary.get('schedule')) if dictionary.get('schedule') else None
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        target_type = dictionary.get('targetType')
        copy_on_run_success = dictionary.get('copyOnRunSuccess')
        config_id = dictionary.get('configId')
        remote_target_config = cohesity_management_sdk.models_v2.cluster_target_configuration.ClusterTargetConfiguration.from_dictionary(dictionary.get('remoteTargetConfig')) if dictionary.get('remoteTargetConfig') else None
        aws_target_config = cohesity_management_sdk.models_v2.aws_target_configuration.AWSTargetConfiguration.from_dictionary(dictionary.get('awsTargetConfig')) if dictionary.get('awsTargetConfig') else None
        azure_target_config = cohesity_management_sdk.models_v2.azure_target_configuration.AzureTargetConfiguration.from_dictionary(dictionary.get('azureTargetConfig')) if dictionary.get('azureTargetConfig') else None

        # Return an object of this model
        return cls(schedule,
                   retention,
                   target_type,
                   copy_on_run_success,
                   config_id,
                   remote_target_config,
                   aws_target_config,
                   azure_target_config)



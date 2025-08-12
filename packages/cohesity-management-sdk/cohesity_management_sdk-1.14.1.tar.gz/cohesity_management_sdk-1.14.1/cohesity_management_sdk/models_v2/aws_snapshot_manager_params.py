# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.ebs_volume_exclusion_params

class AwsSnapshotManagerParams(object):
    """Implementation of the 'AwsSnapshotManagerParams' model.

    Specifies job parameters applicable for all 'kVMware' Environment type Protection Sources in a Protection Job.

    Attributes:
        ami_creation_frequency (int): Specifies the frequency of AMI creation. This should be set if the option to create AMI is set. A value of n creates an AMI from the snapshots after every n runs. eg. n = 2 implies every alternate backup run starting from the first will create an AMI.
        create_ami (bool): If true, creates an AMI after taking snapshots of the instance. It should be set only while backing up EC2 instances. CreateAmi creates AMI for the protection job.
        volume_exclusion_params (EBSVolumeExclusionParams): Specifies the paramaters to exclude volumes attached to EC2 instances at global level.
    """

    _names = {
        "ami_creation_frequency":"amiCreationFrequency",
        "create_ami":"createAmi",
        "volume_exclusion_params":"volumeExclusionParams",
    }

    def __init__(self,
                 ami_creation_frequency=None,
                 create_ami=None,
                 volume_exclusion_params=None):
        """Constructor for the AwsSnapshotManagerParams class"""

        self.ami_creation_frequency = ami_creation_frequency
        self.create_ami = create_ami
        self.volume_exclusion_params = volume_exclusion_params


    @classmethod
    def from_dictionary(cls, dictionary):
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

        ami_creation_frequency = dictionary.get('amiCreationFrequency')
        create_ami = dictionary.get('createAmi')
        volume_exclusion_params = cohesity_management_sdk.models_v2.ebs_volume_exclusion_params.EBSVolumeExclusionParams.from_dictionary(dictionary.get('volumeExclusionParams')) if dictionary.get('volumeExclusionParams') else None

        return cls(
            ami_creation_frequency,
            create_ami,
            volume_exclusion_params
        )
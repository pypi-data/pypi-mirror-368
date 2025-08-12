# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_s_3_protection_group_object_params

class CreateAWSS3ProtectionRequestBody(object):

    """Implementation of the 'CreateAWSS3ProtectionRequestBody' model.

    Specifies the parameters which are specific to AWS related Protection
    Groups using AWS native snapshot orchestration with snapshot manager.
    Atlease one of tags or objects must be specified.

    Attributes:
        backup_object_level_acls (bool): Specifies whether to backup object level acls. Default value
          is false.
        objects (list of AwsS3ProtectionGroupObjectParams): Specifies the objects to be protected.
        skip_on_error (bool): Specifies whether to skip files on error or not. Default value
          is false.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the id of the parent of the objects.
        storage_class (StorageClassEnum): Specifies the AWS S3 Storage classes to backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_object_level_acls":'backupObjectLevelACLs',
        "objects":'objects',
        "skip_on_error":'skipOnError',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "storage_class":'storageClass'
    }

    def __init__(self,
                 backup_object_level_acls=None,
                 objects=None,
                 skip_on_error=None,
                 source_id=None,
                 source_name=None,
                 storage_class=None
                 ):
        """Constructor for the CreateAWSS3ProtectionRequestBody class"""

        # Initialize members of the class
        self.backup_object_level_acls = backup_object_level_acls
        self.objects = objects
        self.skip_on_error = skip_on_error
        self.source_id = source_id
        self.source_name = source_name
        self.storage_class = storage_class




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
        backup_object_level_acls = dictionary.get('backupObjectLevelACLs')
        objects = None
        if dictionary.get("objects") is not None:
            objects =list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.aws_s_3_protection_group_object_params.AWSS3ProtectionGroupObjectParams.from_dictionary(structure))
        skip_on_error = dictionary.get('skipOnError')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        storage_class = dictionary.get('storageClass')

        # Return an object of this model
        return cls(backup_object_level_acls,
                   objects,
                   skip_on_error,
                   source_id,
                   source_name,
                   storage_class)
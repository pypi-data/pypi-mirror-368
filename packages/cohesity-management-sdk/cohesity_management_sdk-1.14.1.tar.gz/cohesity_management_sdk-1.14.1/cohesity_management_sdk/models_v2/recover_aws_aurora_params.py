# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.db_option_group
import cohesity_management_sdk.models_v2.db_parameter_group

class RecoverAWSAuroraParams(object):

    """Implementation of the 'Recover AWS Aurora params.' model.

    Specifies the parameters to recover AWS Aurora.

    Attributes:
        db_port (int): Specifies the port to use for the DB in the restored
            Aurora instance.
        db_instance_id (string): Specifies the DB instance identifier to use
            for the restored DB.
        is_multi_az_deployment (bool): Specifies whether this is a multi-az
            deployment or not.
        enable_public_accessibility (bool): Specifies whether this DB will be
            publicly accessible or not.
        enable_iam_db_authentication (bool): Specifies whether to enable IAM
            authentication for the DB.
        enable_copy_tags_to_snapshots (bool): Specifies whether to enable
            copying of tags to snapshots of the DB.
        enable_auto_minor_version_upgrade (bool): Specifies whether to enable
            auto minor version upgrade in the restored DB.
        db_option_group (DbOptionGroup): Specifies entity representing the
            Aurora option group to use while restoring the DB.
        db_parameter_group (DbParameterGroup): Specifies the entity
            representing the Aurora parameter group to use while restoring the
            DB.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "db_port":'dbPort',
        "db_instance_id":'dbInstanceId',
        "is_multi_az_deployment":'isMultiAzDeployment',
        "enable_iam_db_authentication":'enableIamDbAuthentication',
        "enable_copy_tags_to_snapshots":'enableCopyTagsToSnapshots',
        "enable_auto_minor_version_upgrade":'enableAutoMinorVersionUpgrade',
        "enable_public_accessibility":'enablePublicAccessibility',
        "db_option_group":'dbOptionGroup',
        "db_parameter_group":'dbParameterGroup'
    }

    def __init__(self,
                 db_port=None,
                 db_instance_id=None,
                 is_multi_az_deployment=None,
                 enable_iam_db_authentication=None,
                 enable_copy_tags_to_snapshots=None,
                 enable_auto_minor_version_upgrade=None,
                 enable_public_accessibility=None,
                 db_option_group=None,
                 db_parameter_group=None):
        """Constructor for the RecoverAWSAuroraParams class"""

        # Initialize members of the class
        self.db_port = db_port
        self.db_instance_id = db_instance_id
        self.is_multi_az_deployment = is_multi_az_deployment
        self.enable_public_accessibility = enable_public_accessibility
        self.enable_iam_db_authentication = enable_iam_db_authentication
        self.enable_copy_tags_to_snapshots = enable_copy_tags_to_snapshots
        self.enable_auto_minor_version_upgrade = enable_auto_minor_version_upgrade
        self.db_option_group = db_option_group
        self.db_parameter_group = db_parameter_group


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
        db_port = dictionary.get('dbPort')
        db_instance_id = dictionary.get('dbInstanceId')
        is_multi_az_deployment = dictionary.get('isMultiAzDeployment')
        enable_iam_db_authentication = dictionary.get('enableIamDbAuthentication')
        enable_copy_tags_to_snapshots = dictionary.get('enableCopyTagsToSnapshots')
        enable_auto_minor_version_upgrade = dictionary.get('enableAutoMinorVersionUpgrade')
        enable_public_accessibility = dictionary.get('enablePublicAccessibility')
        db_option_group = cohesity_management_sdk.models_v2.db_option_group.DbOptionGroup.from_dictionary(dictionary.get('dbOptionGroup')) if dictionary.get('dbOptionGroup') else None
        db_parameter_group = cohesity_management_sdk.models_v2.db_parameter_group.DbParameterGroup.from_dictionary(dictionary.get('dbParameterGroup')) if dictionary.get('dbParameterGroup') else None

        # Return an object of this model
        return cls(db_port,
                   db_instance_id,
                   is_multi_az_deployment,
                   enable_iam_db_authentication,
                   enable_copy_tags_to_snapshots,
                   enable_auto_minor_version_upgrade,
                   enable_public_accessibility,
                   db_option_group,
                   db_parameter_group)



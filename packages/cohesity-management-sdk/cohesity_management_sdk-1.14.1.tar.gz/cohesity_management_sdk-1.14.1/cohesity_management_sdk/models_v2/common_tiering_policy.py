# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.file_size_policy
import cohesity_management_sdk.models_v2.file_filtering_policy

class CommonTieringPolicy(object):

    """Implementation of the 'CommonTieringPolicy' model.

    Specifies the common tiering params between uptiering and downtiering.

    Attributes:
        enable_audit_logging (bool): Specifies whether to audit log the file
            tiering activity.
        file_size (FileSizePolicy): Specifies the file's selection rule by
            file size eg. 1. select files greather than 10 Bytes. 2. select
            files less than 20 TiB. 3. select files greather than 5 MiB. type:
            object
        file_path (FileFilteringPolicy): Specifies a set of filters for a file
            based Protection Group. These values are strings which can
            represent a prefix or suffix. Example: '/tmp' or '*.mp4'. For file
            based Protection Groups, all files under prefixes specified by the
            'includeFilters' list will be protected unless they are explicitly
            excluded by the 'excludeFilters' list.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_audit_logging":'enableAuditLogging',
        "file_size":'fileSize',
        "file_path":'filePath'
    }

    def __init__(self,
                 enable_audit_logging=False,
                 file_size=None,
                 file_path=None):
        """Constructor for the CommonTieringPolicy class"""

        # Initialize members of the class
        self.enable_audit_logging = enable_audit_logging
        self.file_size = file_size
        self.file_path = file_path


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
        enable_audit_logging = dictionary.get("enableAuditLogging") if dictionary.get("enableAuditLogging") else False
        file_size = cohesity_management_sdk.models_v2.file_size_policy.FileSizePolicy.from_dictionary(dictionary.get('fileSize')) if dictionary.get('fileSize') else None
        file_path = cohesity_management_sdk.models_v2.file_filtering_policy.FileFilteringPolicy.from_dictionary(dictionary.get('filePath')) if dictionary.get('filePath') else None

        # Return an object of this model
        return cls(enable_audit_logging,
                   file_size,
                   file_path)



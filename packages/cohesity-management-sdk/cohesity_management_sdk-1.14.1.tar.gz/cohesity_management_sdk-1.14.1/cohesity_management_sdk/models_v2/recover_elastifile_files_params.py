# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_file_and_folder_info
import cohesity_management_sdk.models_v2.elastifile_target_params_9
import cohesity_management_sdk.models_v2.flashblade_target_params_1
import cohesity_management_sdk.models_v2.generic_nas_target_params_1
import cohesity_management_sdk.models_v2.gpfs_target_params_1
import cohesity_management_sdk.models_v2.isilon_target_params_1
import cohesity_management_sdk.models_v2.netapp_target_params_3

class RecoverElastifileFilesParams(object):

    """Implementation of the 'Recover Elastifile files Params.' model.

    Specifies the parameters to recover Elastifile files.

    Attributes:
        files_and_folders (list of CommonFileAndFolderInfo): Specifies the
            info about the files and folders to be recovered.
        target_environment (TargetEnvironment1Enum): Specifies the environment
            of the recovery target. The corresponding params below must be
            filled out.
        elastifile_target_params (ElastifileTargetParams9): Specifies the
            params for a Elastifile recovery target.
        flashblade_target_params (FlashbladeTargetParams1): Specifies the
            params for a Flashblade recovery target.
        generic_nas_target_params (GenericNasTargetParams1): Specifies the
            params for a generic NAS recovery target.
        gpfs_target_params (GpfsTargetParams1): Specifies the params for a
            GPFS recovery target.
        isilon_target_params (IsilonTargetParams1): Specifies the params for
            an Isilon recovery target.
        netapp_target_params (NetappTargetParams3): Specifies the params for
            an Netapp recovery target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "files_and_folders":'filesAndFolders',
        "target_environment":'targetEnvironment',
        "elastifile_target_params":'elastifileTargetParams',
        "flashblade_target_params":'flashbladeTargetParams',
        "generic_nas_target_params":'genericNasTargetParams',
        "gpfs_target_params":'gpfsTargetParams',
        "isilon_target_params":'isilonTargetParams',
        "netapp_target_params":'netappTargetParams'
    }

    def __init__(self,
                 files_and_folders=None,
                 target_environment=None,
                 elastifile_target_params=None,
                 flashblade_target_params=None,
                 generic_nas_target_params=None,
                 gpfs_target_params=None,
                 isilon_target_params=None,
                 netapp_target_params=None):
        """Constructor for the RecoverElastifileFilesParams class"""

        # Initialize members of the class
        self.files_and_folders = files_and_folders
        self.target_environment = target_environment
        self.elastifile_target_params = elastifile_target_params
        self.flashblade_target_params = flashblade_target_params
        self.generic_nas_target_params = generic_nas_target_params
        self.gpfs_target_params = gpfs_target_params
        self.isilon_target_params = isilon_target_params
        self.netapp_target_params = netapp_target_params


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
        files_and_folders = None
        if dictionary.get("filesAndFolders") is not None:
            files_and_folders = list()
            for structure in dictionary.get('filesAndFolders'):
                files_and_folders.append(cohesity_management_sdk.models_v2.common_file_and_folder_info.CommonFileAndFolderInfo.from_dictionary(structure))
        target_environment = dictionary.get('targetEnvironment')
        elastifile_target_params = cohesity_management_sdk.models_v2.elastifile_target_params_9.ElastifileTargetParams9.from_dictionary(dictionary.get('elastifileTargetParams')) if dictionary.get('elastifileTargetParams') else None
        flashblade_target_params = cohesity_management_sdk.models_v2.flashblade_target_params_1.FlashbladeTargetParams1.from_dictionary(dictionary.get('flashbladeTargetParams')) if dictionary.get('flashbladeTargetParams') else None
        generic_nas_target_params = cohesity_management_sdk.models_v2.generic_nas_target_params_1.GenericNasTargetParams1.from_dictionary(dictionary.get('genericNasTargetParams')) if dictionary.get('genericNasTargetParams') else None
        gpfs_target_params = cohesity_management_sdk.models_v2.gpfs_target_params_1.GpfsTargetParams1.from_dictionary(dictionary.get('gpfsTargetParams')) if dictionary.get('gpfsTargetParams') else None
        isilon_target_params = cohesity_management_sdk.models_v2.isilon_target_params_1.IsilonTargetParams1.from_dictionary(dictionary.get('isilonTargetParams')) if dictionary.get('isilonTargetParams') else None
        netapp_target_params = cohesity_management_sdk.models_v2.netapp_target_params_3.NetappTargetParams3.from_dictionary(dictionary.get('netappTargetParams')) if dictionary.get('netappTargetParams') else None

        # Return an object of this model
        return cls(files_and_folders,
                   target_environment,
                   elastifile_target_params,
                   flashblade_target_params,
                   generic_nas_target_params,
                   gpfs_target_params,
                   isilon_target_params,
                   netapp_target_params)



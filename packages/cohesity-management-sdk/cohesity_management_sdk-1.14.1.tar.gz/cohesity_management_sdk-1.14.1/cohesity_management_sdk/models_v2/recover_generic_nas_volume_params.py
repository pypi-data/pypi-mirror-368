# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.generic_nas_target_params_2
import cohesity_management_sdk.models_v2.elastifile_target_params_2
import cohesity_management_sdk.models_v2.flashblade_target_params
import cohesity_management_sdk.models_v2.gpfs_target_params
import cohesity_management_sdk.models_v2.isilon_target_params
import cohesity_management_sdk.models_v2.netapp_target_params_2
import cohesity_management_sdk.models_v2.view_target_params

class RecoverGenericNASVolumeParams(object):

    """Implementation of the 'Recover Generic NAS Volume Params.' model.

    Specifies the parameters to recover Generic NAS volumes.

    Attributes:
        target_environment (TargetEnvironmentEnum): Specifies the environment
            of the recovery target. The corresponding params below must be
            filled out.
        generic_nas_target_params (GenericNasTargetParams2): Specifies the
            params for a Generic NAS recovery target.
        elastifile_target_params (ElastifileTargetParams2): Specifies the
            params for a Elastifile recovery target.
        flashblade_target_params (FlashbladeTargetParams): Specifies the
            params for a Flashblade recovery target.
        gpfs_target_params (GpfsTargetParams): Specifies the params for a GPFS
            recovery target.
        isilon_target_params (IsilonTargetParams): Specifies the params for an
            Isilon recovery target.
        netapp_target_params (NetappTargetParams2): Specifies the params for
            an Netapp recovery target.
        view_target_params (ViewTargetParams): Specifies the params for a
            Cohesity view recovery target.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "generic_nas_target_params":'genericNasTargetParams',
        "elastifile_target_params":'elastifileTargetParams',
        "flashblade_target_params":'flashbladeTargetParams',
        "gpfs_target_params":'gpfsTargetParams',
        "isilon_target_params":'isilonTargetParams',
        "netapp_target_params":'netappTargetParams',
        "view_target_params":'viewTargetParams'
    }

    def __init__(self,
                 target_environment=None,
                 generic_nas_target_params=None,
                 elastifile_target_params=None,
                 flashblade_target_params=None,
                 gpfs_target_params=None,
                 isilon_target_params=None,
                 netapp_target_params=None,
                 view_target_params=None):
        """Constructor for the RecoverGenericNASVolumeParams class"""

        # Initialize members of the class
        self.target_environment = target_environment
        self.generic_nas_target_params = generic_nas_target_params
        self.elastifile_target_params = elastifile_target_params
        self.flashblade_target_params = flashblade_target_params
        self.gpfs_target_params = gpfs_target_params
        self.isilon_target_params = isilon_target_params
        self.netapp_target_params = netapp_target_params
        self.view_target_params = view_target_params


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
        target_environment = dictionary.get('targetEnvironment')
        generic_nas_target_params = cohesity_management_sdk.models_v2.generic_nas_target_params_2.GenericNasTargetParams2.from_dictionary(dictionary.get('genericNasTargetParams')) if dictionary.get('genericNasTargetParams') else None
        elastifile_target_params = cohesity_management_sdk.models_v2.elastifile_target_params_2.ElastifileTargetParams2.from_dictionary(dictionary.get('elastifileTargetParams')) if dictionary.get('elastifileTargetParams') else None
        flashblade_target_params = cohesity_management_sdk.models_v2.flashblade_target_params.FlashbladeTargetParams.from_dictionary(dictionary.get('flashbladeTargetParams')) if dictionary.get('flashbladeTargetParams') else None
        gpfs_target_params = cohesity_management_sdk.models_v2.gpfs_target_params.GpfsTargetParams.from_dictionary(dictionary.get('gpfsTargetParams')) if dictionary.get('gpfsTargetParams') else None
        isilon_target_params = cohesity_management_sdk.models_v2.isilon_target_params.IsilonTargetParams.from_dictionary(dictionary.get('isilonTargetParams')) if dictionary.get('isilonTargetParams') else None
        netapp_target_params = cohesity_management_sdk.models_v2.netapp_target_params_2.NetappTargetParams2.from_dictionary(dictionary.get('netappTargetParams')) if dictionary.get('netappTargetParams') else None
        view_target_params = cohesity_management_sdk.models_v2.view_target_params.ViewTargetParams.from_dictionary(dictionary.get('viewTargetParams')) if dictionary.get('viewTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   generic_nas_target_params,
                   elastifile_target_params,
                   flashblade_target_params,
                   gpfs_target_params,
                   isilon_target_params,
                   netapp_target_params,
                   view_target_params)



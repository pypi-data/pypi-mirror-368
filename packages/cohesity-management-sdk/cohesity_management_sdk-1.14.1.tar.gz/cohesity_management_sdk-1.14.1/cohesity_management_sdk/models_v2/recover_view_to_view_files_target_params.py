# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_to_view_files_target_params
import cohesity_management_sdk.models_v2.recover_to_original_view_files_target_params

class RecoverViewToViewFilesTargetParams(object):
    """Implementation of the 'RecoverViewToViewFilesTargetParams' model.

    Specifies the params of the View recovery target.

    Attributes:
        new_view_config (RecoverToViewFilesTargetParams): Specifies the new destination View configuration parameters where the files will be recovered. This is mandatory if recoverToNewView is set to true.
        original_view_config (RecoverToOriginalViewFilesTargetParams): Specifies the View configuration if files are being recovered to original View. If not specified, all the configuration parameters will be retained.
        recover_to_new_view (bool): Specifies the parameter whether the recovery should be performed to a new or the original View target.
        view_id (long|int): Specifies the ID of the view.
        view_name (string): Specifies the name of the new view that's the target for recovery.
    """

    _names = {
        "new_view_config":"newViewConfig",
        "original_view_config":"originalViewConfig",
        "recover_to_new_view":"recoverToNewView",
        "view_id":"viewId",
        "view_name":"viewName",
    }

    def __init__(self,
                 new_view_config=None,
                 original_view_config=None,
                 recover_to_new_view=None,
                 view_id=None,
                 view_name=None):
        """Constructor for the RecoverViewToViewFilesTargetParams class"""

        self.new_view_config = new_view_config
        self.original_view_config = original_view_config
        self.recover_to_new_view = recover_to_new_view
        self.view_id = view_id
        self.view_name = view_name


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

        new_view_config = cohesity_management_sdk.models_v2.recover_to_view_files_target_params.RecoverToViewFilesTargetParams.from_dictionary(dictionary.get('newViewConfig')) if dictionary.get('newViewConfig') else None
        original_view_config = cohesity_management_sdk.models_v2.recover_to_original_view_files_target_params.RecoverToOriginalViewFilesTargetParams.from_dictionary(dictionary.get('originalViewConfig')) if dictionary.get('originalViewConfig') else None
        recover_to_new_view = dictionary.get('recoverToNewView')
        view_id = dictionary.get('viewId')
        view_name = dictionary.get('viewName')

        return cls(
            new_view_config,
            original_view_config,
            recover_to_new_view,
            view_id,
            view_name
        )
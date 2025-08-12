# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.one_drive_param

class ObjectSiteParam(object):

    """Implementation of the 'ObjectSiteParam' model.

    Specifies Site recovery parameters.

    Attributes:
        document_library_params (list of OneDriveParam): Specifies the parameters to recover a document library
        owner_info (CommonRecoverObjectSnapshotParams): Specifies the Site owner info.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "document_library_params":'documentLibraryParams',
        "owner_info":'ownerInfo'
    }

    def __init__(self,
                 document_library_params=None,
                 owner_info=None
                 ):
        """Constructor for the ObjectSiteParam class"""

        # Initialize members of the class
        self.document_library_params = document_library_params
        self.owner_info = owner_info


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
        document_library_params = None
        if dictionary.get('documentLibraryParams') is not None:
            document_library_params = list()
            for structure in dictionary.get('documentLibraryParams'):
                document_library_params.append(cohesity_management_sdk.models_v2.one_drive_param.OneDriveParam.from_dictionary(structure))
        owner_info = cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(dictionary.get('ownerInfo')) if dictionary.get('ownerInfo') else None

        # Return an object of this model
        return cls(document_library_params,
                   owner_info)
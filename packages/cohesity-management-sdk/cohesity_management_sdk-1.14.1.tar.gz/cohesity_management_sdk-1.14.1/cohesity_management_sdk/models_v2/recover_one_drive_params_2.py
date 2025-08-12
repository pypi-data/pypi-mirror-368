# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_one_drive_param
import cohesity_management_sdk.models_v2.target_one_drive_param

class RecoverOneDriveParams2(object):

    """Implementation of the 'RecoverOneDriveParams2' model.

    Specifies the parameters to recover Office 365 One Drive.

    Attributes:
        objects (list of ObjectOneDriveParam): Specifies a list of OneDrive
            params associated with the objects to recover.
        target_drive (TargetOneDriveParam): Specifies the target OneDrive to
            recover to. If not specified, the objects will be recovered to
            original location.
        continue_on_error (bool): Specifies whether to continue recovering
            other OneDrive items if one of items failed to recover. Default
            value is false.
        recover_preservation_hold_library (bool): Specifies whether to recover Preservation Hold Library associated
          with the OneDrives selected for restore. Default value is false.
        recover_user_default_drive (bool): Specifies whether to recover default drives associated with the
          OneDrives selected for restore. Default value is true. This setting can
          be overridden for each object selected for recovery, by specifying 'recoverEntireDrive'
          for the desired drive within 'oneDriveParams'. Granular recovery is still
          allowed even if this value is set to true.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "target_drive":'targetDrive',
        "continue_on_error":'continueOnError',
        "recover_preservation_hold_library":'recoverPreservationHoldLibrary',
        "recover_user_default_drive":'recoverUserDefaultDrive'
    }

    def __init__(self,
                 objects=None,
                 target_drive=None,
                 continue_on_error=None,
                 recover_preservation_hold_library=None,
                 recover_user_default_drive=None):
        """Constructor for the RecoverOneDriveParams2 class"""

        # Initialize members of the class
        self.objects = objects
        self.target_drive = target_drive
        self.continue_on_error = continue_on_error
        self.recover_preservation_hold_library = recover_preservation_hold_library
        self.recover_user_default_drive = recover_user_default_drive


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
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.object_one_drive_param.ObjectOneDriveParam.from_dictionary(structure))
        target_drive = cohesity_management_sdk.models_v2.target_one_drive_param.TargetOneDriveParam.from_dictionary(dictionary.get('targetDrive')) if dictionary.get('targetDrive') else None
        continue_on_error = dictionary.get('continueOnError')
        recover_preservation_hold_library = dictionary.get('recoverPreservationHoldLibrary')
        recover_user_default_drive = dictionary.get('recoverUserDefaultDrive')

        # Return an object of this model
        return cls(objects,
                   target_drive,
                   continue_on_error,
                   recover_preservation_hold_library,
                   recover_user_default_drive)
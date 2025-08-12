# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.source_15
import cohesity_management_sdk.models_v2.rename_recovered_volume_params

class NewSourceConfig23(object):

    """Implementation of the 'NewSourceConfig23' model.

    Specifies the new destination Source configuration parameters where the
    Pure volume will be recovered. This is mandatory if recoverToNewSource is
    set to true.

    Attributes:
        source (Source15): Specifies the id of the new target parent source to
            recover the Pure SAN Volume to. This field must be specified if
            recoverToNewSource is true.
        rename_recovered_volume_params (RenameRecoveredVolumeParams):
            Specifies params to rename the recovered SAN volumes. If not
            specified, the original names of the volumes are preserved.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source":'source',
        "rename_recovered_volume_params":'renameRecoveredVolumeParams'
    }

    def __init__(self,
                 source=None,
                 rename_recovered_volume_params=None):
        """Constructor for the NewSourceConfig23 class"""

        # Initialize members of the class
        self.source = source
        self.rename_recovered_volume_params = rename_recovered_volume_params


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
        source = cohesity_management_sdk.models_v2.source_15.Source15.from_dictionary(dictionary.get('source')) if dictionary.get('source') else None
        rename_recovered_volume_params = cohesity_management_sdk.models_v2.rename_recovered_volume_params.RenameRecoveredVolumeParams.from_dictionary(dictionary.get('renameRecoveredVolumeParams')) if dictionary.get('renameRecoveredVolumeParams') else None

        # Return an object of this model
        return cls(source,
                   rename_recovered_volume_params)
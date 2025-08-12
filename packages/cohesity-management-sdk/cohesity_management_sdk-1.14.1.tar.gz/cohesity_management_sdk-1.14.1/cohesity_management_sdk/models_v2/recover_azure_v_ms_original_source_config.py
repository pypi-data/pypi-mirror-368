# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.data_transfer_info_request

class RecoverAzureVMsOriginalSourceConfig(object):

    """Implementation of the 'Recover Azure VMs Original Source Config.' model.

    Specifies the Source configuration if VM's are being recovered to
      Original Source.

    Attributes:
        data_transfer_Info (DataTransferInfoRequest): Specifies the id of the parent source to recover the
            VMs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "data_transfer_info":'dataTransferInfo'
    }

    def __init__(self,
                 data_transfer_info=None):
        """Constructor for the RecoverAzureVMsOriginalSourceConfig class"""

        # Initialize members of the class
        self.data_transfer_info = data_transfer_info


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
        data_transfer_info = cohesity_management_sdk.models_v2.data_transfer_info_request.DataTransferInfoRequest.from_dictionary(dictionary.get('dataTransferInfo')) if dictionary.get('dataTransferInfo') else None

        # Return an object of this model
        return cls(data_transfer_info)
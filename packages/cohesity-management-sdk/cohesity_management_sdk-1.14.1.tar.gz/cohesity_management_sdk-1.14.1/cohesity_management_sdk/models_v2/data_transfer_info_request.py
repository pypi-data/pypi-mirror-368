# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.private_network_info

class DataTransferInfoRequest(object):

    """Implementation of the 'DataTransferInfoRequest' model.

    Specifies the the details of network used in transferring the data
      from source account to Cohesity cluster.

    Attributes:
        is_private_network (bool): Specifies whether to use private network or public network.
        private_network_info_list (list of PrivateNetworkInfo): Specifies Information required to create endpoints in private
          networks for all regions whose VMs are getting protected.
        use_protection_job_info (bool): Specifies Whether to use private network info which was used
          in backup of VMs.This should be populated only for restore job.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_private_network":'isPrivateNetwork',
        "private_network_info_list":'privateNetworkInfoList',
        "use_protection_job_info":'useProtectionJobInfo'
    }

    def __init__(self,
                 is_private_network=None,
                 private_network_info_list=None,
                 use_protection_job_info=None
                 ):
        """Constructor for the DataTransferInfoRequest class"""

        # Initialize members of the class
        self.is_private_network = is_private_network
        self.private_network_info_list = private_network_info_list
        self.use_protection_job_info = use_protection_job_info


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
        is_private_network = dictionary.get('isPrivateNetwork')
        private_network_info_list = None
        if dictionary.get("privateNetworkInfoList") is not None:
            private_network_info_list = list()
            for structure in dictionary.get('privateNetworkInfoList'):
                private_network_info_list.append(cohesity_management_sdk.models_v2.private_network_info.PrivateNetworkInfo.from_dictionary(structure))
        use_protection_job_info = dictionary.get('useProtectionJobInfo')

        # Return an object of this model
        return cls(is_private_network,
                   private_network_info_list,
                   use_protection_job_info)
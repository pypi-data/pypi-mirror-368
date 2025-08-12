# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_target_params_12

class OnpremDeployParams(object):

    """Implementation of the 'OnpremDeployParams' model.

    Specifies the details about OnpremDeploy target where backup snapshots
      may be converted and deployed.

    Attributes:
        id (long|int): Specifies the unique id of the onprem entity.
        restore_vmware_params (VMwareTargetParams12): Specifies information needed to identify various resources when
          deploying VMs to OnPrem sources like VMware..


    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "restore_vmware_params":'restoreVMwareParams'
    }

    def __init__(self,
                 id=None,
                 restore_vmware_params=None
                 ):
        """Constructor for the CloudSpinTargetConfiguration class"""

        # Initialize members of the class
        self.id = id
        self.restore_vmware_params = restore_vmware_params


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
        id = dictionary.get('id')
        restore_vmware_params = cohesity_management_sdk.models_v2.vmware_target_params_12.VmwareTargetParams12.from_dictionary(dictionary.get('restoreVMwareParams')) if dictionary.get('restoreVMwareParams') else None


        # Return an object of this model
        return cls(
                   id,
                   restore_vmware_params)
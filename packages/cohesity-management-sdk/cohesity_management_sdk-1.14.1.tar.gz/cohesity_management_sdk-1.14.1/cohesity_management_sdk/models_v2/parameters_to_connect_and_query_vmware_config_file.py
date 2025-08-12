# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.parameters_to_connect_and_query_vmware_config_file_1

class ParametersToConnectAndQueryVmwareConfigFile(object):

    """Implementation of the 'Parameters to connect and query VMware config file.' model.

    Specifies the parameters to connect to a seed node and fetch information
    from its config file.

    Attributes:
        mtype (Type57Enum): Specifies the VMware Source type.
        vcd_params (ParametersToConnectAndQueryVmwareConfigFile1): Specifies
            the parameters to connect to a seed node and fetch information
            from its config file.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "vcd_params":'vcdParams'
    }

    def __init__(self,
                 mtype=None,
                 vcd_params=None):
        """Constructor for the ParametersToConnectAndQueryVmwareConfigFile class"""

        # Initialize members of the class
        self.mtype = mtype
        self.vcd_params = vcd_params


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
        mtype = dictionary.get('type')
        vcd_params = cohesity_management_sdk.models_v2.parameters_to_connect_and_query_vmware_config_file_1.ParametersToConnectAndQueryVmwareConfigFile1.from_dictionary(dictionary.get('vcdParams')) if dictionary.get('vcdParams') else None

        # Return an object of this model
        return cls(mtype,
                   vcd_params)



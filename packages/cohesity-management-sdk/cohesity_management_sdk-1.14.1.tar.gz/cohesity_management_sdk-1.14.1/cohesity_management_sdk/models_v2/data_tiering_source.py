# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.generic_nas_data_tiering_params
import cohesity_management_sdk.models_v2.isilon_data_tiering_params
import cohesity_management_sdk.models_v2.netapp_data_tiering_params

class DataTieringSource(object):

    """Implementation of the 'DataTieringSource' model.

    Specifies the source data tiering details.

    Attributes:
        environment (Environment3Enum): Specifies the environment type of the
            data tiering source.
        generic_nas_params (GenericNasDataTieringParams): Specifies the
            parameters which are specific to NAS related Protection Groups.
        isilon_params (IsilonDataTieringParams): Specifies the parameters
            which are specific to Isilon related Protection Groups.
        netapp_params (NetappDataTieringParams): Specifies the parameters
            which are specific to Netapp related Protection Groups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "generic_nas_params":'genericNasParams',
        "isilon_params":'isilonParams',
        "netapp_params":'netappParams'
    }

    def __init__(self,
                 environment=None,
                 generic_nas_params=None,
                 isilon_params=None,
                 netapp_params=None):
        """Constructor for the DataTieringSource class"""

        # Initialize members of the class
        self.environment = environment
        self.generic_nas_params = generic_nas_params
        self.isilon_params = isilon_params
        self.netapp_params = netapp_params


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
        environment = dictionary.get('environment')
        generic_nas_params = cohesity_management_sdk.models_v2.generic_nas_data_tiering_params.GenericNasDataTieringParams.from_dictionary(dictionary.get('genericNasParams')) if dictionary.get('genericNasParams') else None
        isilon_params = cohesity_management_sdk.models_v2.isilon_data_tiering_params.IsilonDataTieringParams.from_dictionary(dictionary.get('isilonParams')) if dictionary.get('isilonParams') else None
        netapp_params = cohesity_management_sdk.models_v2.netapp_data_tiering_params.NetappDataTieringParams.from_dictionary(dictionary.get('netappParams')) if dictionary.get('netappParams') else None

        # Return an object of this model
        return cls(environment,
                   generic_nas_params,
                   isilon_params,
                   netapp_params)



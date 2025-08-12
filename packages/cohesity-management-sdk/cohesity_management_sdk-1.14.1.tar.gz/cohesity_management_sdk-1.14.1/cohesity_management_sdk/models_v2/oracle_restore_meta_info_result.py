# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.key_value_pair

class OracleRestoreMetaInfoResult(object):

    """Implementation of the 'OracleRestoreMetaInfoResult' model.

    Result to store oracle meta-info from snapshot id and other oracle
    params.

    Attributes:
        restricted_pfile_param_map (list of KeyValuePair): Specifies map for
            restricted pfile params.
        inherited_pfile_param_map (list of KeyValuePair): Specifies map for
            inherited pfile params.
        cohesity_pfile_param_map (list of KeyValuePair): Specifies map for
            cohesity controlled pfile params.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "restricted_pfile_param_map":'restrictedPfileParamMap',
        "inherited_pfile_param_map":'inheritedPfileParamMap',
        "cohesity_pfile_param_map":'cohesityPfileParamMap'
    }

    def __init__(self,
                 restricted_pfile_param_map=None,
                 inherited_pfile_param_map=None,
                 cohesity_pfile_param_map=None):
        """Constructor for the OracleRestoreMetaInfoResult class"""

        # Initialize members of the class
        self.restricted_pfile_param_map = restricted_pfile_param_map
        self.inherited_pfile_param_map = inherited_pfile_param_map
        self.cohesity_pfile_param_map = cohesity_pfile_param_map


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
        restricted_pfile_param_map = None
        if dictionary.get("restrictedPfileParamMap") is not None:
            restricted_pfile_param_map = list()
            for structure in dictionary.get('restrictedPfileParamMap'):
                restricted_pfile_param_map.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        inherited_pfile_param_map = None
        if dictionary.get("inheritedPfileParamMap") is not None:
            inherited_pfile_param_map = list()
            for structure in dictionary.get('inheritedPfileParamMap'):
                inherited_pfile_param_map.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))
        cohesity_pfile_param_map = None
        if dictionary.get("cohesityPfileParamMap") is not None:
            cohesity_pfile_param_map = list()
            for structure in dictionary.get('cohesityPfileParamMap'):
                cohesity_pfile_param_map.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))

        # Return an object of this model
        return cls(restricted_pfile_param_map,
                   inherited_pfile_param_map,
                   cohesity_pfile_param_map)



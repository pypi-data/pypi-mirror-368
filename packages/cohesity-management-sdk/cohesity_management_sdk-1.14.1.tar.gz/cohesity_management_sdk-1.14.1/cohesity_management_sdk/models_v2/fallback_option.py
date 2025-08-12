# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.fixed_type_params

class FallbackOption(object):

    """Implementation of the 'FallbackOption' model.

    Specifies a fallback user id mapping param in case the primary config does
    not work.

    Attributes:
        mtype (Type1Enum): Specifies the type of the mapping.
        fixed_type_params (FixedTypeParams): Specifies the params for Fixed
            mapping type mapping.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "fixed_type_params":'fixedTypeParams'
    }

    def __init__(self,
                 mtype=None,
                 fixed_type_params=None):
        """Constructor for the FallbackOption class"""

        # Initialize members of the class
        self.mtype = mtype
        self.fixed_type_params = fixed_type_params


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
        fixed_type_params = cohesity_management_sdk.models_v2.fixed_type_params.FixedTypeParams.from_dictionary(dictionary.get('fixedTypeParams')) if dictionary.get('fixedTypeParams') else None

        # Return an object of this model
        return cls(mtype,
                   fixed_type_params)



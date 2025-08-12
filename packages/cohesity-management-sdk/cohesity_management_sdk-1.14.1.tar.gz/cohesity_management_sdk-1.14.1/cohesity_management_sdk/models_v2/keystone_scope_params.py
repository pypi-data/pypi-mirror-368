# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.project_scope_params_2
import cohesity_management_sdk.models_v2.domain_scope_params_2

class KeystoneScopeParams(object):

    """Implementation of the 'KeystoneScopeParams' model.

    Specifies scope paramteres of a Keystone.

    Attributes:
        mtype (Type12Enum): Specifies the scope type.
        project_scope_params (ProjectScopeParams2): Specifies the parameter
            for project type scope.
        domain_scope_params (DomainScopeParams2): Specifies the parameters for
            domain type scope.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "project_scope_params":'projectScopeParams',
        "domain_scope_params":'domainScopeParams'
    }

    def __init__(self,
                 mtype=None,
                 project_scope_params=None,
                 domain_scope_params=None):
        """Constructor for the KeystoneScopeParams class"""

        # Initialize members of the class
        self.mtype = mtype
        self.project_scope_params = project_scope_params
        self.domain_scope_params = domain_scope_params


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
        project_scope_params = cohesity_management_sdk.models_v2.project_scope_params_2.ProjectScopeParams2.from_dictionary(dictionary.get('projectScopeParams')) if dictionary.get('projectScopeParams') else None
        domain_scope_params = cohesity_management_sdk.models_v2.domain_scope_params_2.DomainScopeParams2.from_dictionary(dictionary.get('domainScopeParams')) if dictionary.get('domainScopeParams') else None

        # Return an object of this model
        return cls(mtype,
                   project_scope_params,
                   domain_scope_params)



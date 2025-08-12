# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.ms_group_param

class RecoverMsGroupParams(object):

    """Implementation of the 'RecoverMsGroupParams' model.

    Specifies the parameters to recover Microsoft 365 Group.

    Attributes:
        ms_groups (list of MsGroupParam): Specifies a list of groups getting
            restored.
        restore_to_original (bool): Specifies whether or not all groups are
            restored to original location.
        target_group (string): Specifies target group nickname in case
            restoreToOriginal is false. This needs to be specifid when
            restoreToOriginal is false.
        target_group_name (string): Specifies target group name in case
            restore_to_original is false. This needs to be specifid when
            restoreToOriginal is false. However, this will be ignored if
            restoring to alternate existing group (i.e. to a group the
            nickname of which is same as the one supplied by the end user).
        continue_on_error (bool): Specifies whether to continue recovering
            other MS groups if one of MS groups failed to recover. Default
            value is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ms_groups":'msGroups',
        "restore_to_original":'restoreToOriginal',
        "target_group":'targetGroup',
        "target_group_name":'targetGroupName',
        "continue_on_error":'continueOnError'
    }

    def __init__(self,
                 ms_groups=None,
                 restore_to_original=None,
                 target_group=None,
                 target_group_name=None,
                 continue_on_error=None):
        """Constructor for the RecoverMsGroupParams class"""

        # Initialize members of the class
        self.ms_groups = ms_groups
        self.restore_to_original = restore_to_original
        self.target_group = target_group
        self.target_group_name = target_group_name
        self.continue_on_error = continue_on_error


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
        ms_groups = None
        if dictionary.get("msGroups") is not None:
            ms_groups = list()
            for structure in dictionary.get('msGroups'):
                ms_groups.append(cohesity_management_sdk.models_v2.ms_group_param.MsGroupParam.from_dictionary(structure))
        restore_to_original = dictionary.get('restoreToOriginal')
        target_group = dictionary.get('targetGroup')
        target_group_name = dictionary.get('targetGroupName')
        continue_on_error = dictionary.get('continueOnError')

        # Return an object of this model
        return cls(ms_groups,
                   restore_to_original,
                   target_group,
                   target_group_name,
                   continue_on_error)



# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.tdm_task
import cohesity_management_sdk.models_v2.pagination_info

class TdmTasks(object):

    """Implementation of the 'TdmTasks' model.

    Specifies a collection of TDM tasks.

    Attributes:
        tasks (list of TdmTask): Specifies the collection of TDM tasks,
            filtered by the specified criteria.
        pagination_info (PaginationInfo): Specifies information needed to
            support pagination.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tasks":'tasks',
        "pagination_info":'paginationInfo'
    }

    def __init__(self,
                 tasks=None,
                 pagination_info=None):
        """Constructor for the TdmTasks class"""

        # Initialize members of the class
        self.tasks = tasks
        self.pagination_info = pagination_info


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
        tasks = None
        if dictionary.get("tasks") is not None:
            tasks = list()
            for structure in dictionary.get('tasks'):
                tasks.append(cohesity_management_sdk.models_v2.tdm_task.TdmTask.from_dictionary(structure))
        pagination_info = cohesity_management_sdk.models_v2.pagination_info.PaginationInfo.from_dictionary(dictionary.get('paginationInfo')) if dictionary.get('paginationInfo') else None

        # Return an object of this model
        return cls(tasks,
                   pagination_info)



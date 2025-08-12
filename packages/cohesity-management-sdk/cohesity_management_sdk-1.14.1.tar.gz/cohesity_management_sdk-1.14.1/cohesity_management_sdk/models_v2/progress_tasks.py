# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.progress_task

class ProgressTasks(object):

    """Implementation of the 'Progress Tasks' model.

    List of Progress Tasks.

    Attributes:
        progress_tasks (list of ProgressTask): Specifies the list of Progress
            Task.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "progress_tasks":'progressTasks'
    }

    def __init__(self,
                 progress_tasks=None):
        """Constructor for the ProgressTasks class"""

        # Initialize members of the class
        self.progress_tasks = progress_tasks


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
        progress_tasks = None
        if dictionary.get("progressTasks") is not None:
            progress_tasks = list()
            for structure in dictionary.get('progressTasks'):
                progress_tasks.append(cohesity_management_sdk.models_v2.progress_task.ProgressTask.from_dictionary(structure))

        # Return an object of this model
        return cls(progress_tasks)



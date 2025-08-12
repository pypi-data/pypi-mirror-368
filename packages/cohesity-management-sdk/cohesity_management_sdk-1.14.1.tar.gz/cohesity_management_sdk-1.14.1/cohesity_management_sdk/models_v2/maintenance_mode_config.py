# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.schedule_2
import cohesity_management_sdk.models_v2.time_range_usecs
import cohesity_management_sdk.models_v2.workflow_intervention_spec

class MaintenanceModeConfig(object):

    """Implementation of the 'MaintenanceModeConfig' model.

    Specifies the entity metadata for maintenance mode.

    Attributes:
        activation_time_intervals (list of TimeRangeUsecs): Specifies the absolute intervals where the maintenance schedule
          is valid, i.e. maintenance_shedule is considered only for these time ranges.
          (For example, if there is one time range with [now_usecs, now_usecs + 10
          days], the action will be done during the maintenance_schedule for the next
          10 days.)The start time must be specified. The end time can be -1 which
          would denote an indefinite maintenance mode.
        maintenance_schedule (Schedule2): Specifies the schedule to be followed in the activationTimeIntervals.
        user_message (string): User provided message associated with this maintenance mode.
        workflow_intervention_spec_list (list of WorkflowInterventionSpec): Specifies the type of intervention for different workflows when
          the source goes into maintenance mode.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "activation_time_intervals":'activationTimeIntervals',
        "maintenance_schedule":'maintenanceSchedule',
        "user_message":'userMessage',
        "workflow_intervention_spec_list":'workflowInterventionSpecList'
    }

    def __init__(self,
                 activation_time_intervals=None,
                 maintenance_schedule=None,
                 user_message=None,
                 workflow_intervention_spec_list=None):
        """Constructor for the MaintenanceModeConfig class"""

        # Initialize members of the class
        self.activation_time_intervals = activation_time_intervals
        self.maintenance_schedule = maintenance_schedule
        self.user_message = user_message
        self.workflow_intervention_spec_list = workflow_intervention_spec_list


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
        activation_time_intervals = None
        if dictionary.get('activationTimeIntervals') is not None:
            activation_time_intervals = list()
            for structure in dictionary.get('activationTimeIntervals'):
                activation_time_intervals.append(cohesity_management_sdk.models_v2.time_range_usecs.TimeRangeUsecs.from_dictionary(structure))
        maintenance_schedule = cohesity_management_sdk.models_v2.schedule_2.Schedule2.from_dictionary(
            dictionary.get('maintenanceSchedule')) if dictionary.get('maintenanceSchedule') else None
        user_message = dictionary.get('userMessage')
        workflow_intervention_spec_list = None
        if dictionary.get('workflowInterventionSpecList') is not None:
            workflow_intervention_spec_list = list()
            for structure in dictionary.get('workflowInterventionSpecList'):
                for structure in dictionary.get('workflowInterventionSpecList'):
                    workflow_intervention_spec_list.append(cohesity_management_sdk.models_v2.workflow_intervention_spec.WorkflowInterventionSpec.from_dictionary(structure))


        # Return an object of this model
        return cls(activation_time_intervals, maintenance_schedule, user_message, workflow_intervention_spec_list)
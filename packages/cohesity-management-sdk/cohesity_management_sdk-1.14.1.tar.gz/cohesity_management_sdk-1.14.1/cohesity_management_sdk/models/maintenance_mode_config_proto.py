# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.time_range_usecs
import cohesity_management_sdk.models.maintenance_mode_config_proto_workflow_intervention_spec
import cohesity_management_sdk.models.schedule_proto

class MaintenanceModeConfigProto(object):

    """Implementation of the 'MaintenanceModeConfigProto' model.

    Specifies the parameters for configuration of IPMI. This is only needed
    for physical clusters.

    Attributes:
        activation_time_intervals (list of TimeRangeUsecs): This specifies
            the absolute intervals where the maintenance schedule is
            valid, i.e. maintenance_shedule is considered only for these time
            ranges.
        maintenance_schedule (ScheduleProto): The schedule to be followed
            in the activation_time_intervals.
        user_message (string): User provided message associated with this
            maintenance mode.
        workflow_intervention_spec_vec (list of
            MaintenanceModeConfigProto_WorkflowInterventionSpec): The type of
            intervention for different workflows when the source goes
            into maintenance mode. By default, the workflows not in this vec have
            kNoIntervention, i.e., the workflow will proceed to completion.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "activation_time_intervals":'activationTimeIntervals',
        "maintenance_schedule":'maintenanceSchedule',
        "user_message":'userMessage',
        "workflow_intervention_spec_vec":'workflowInterventionSpecVec'
    }

    def __init__(self,
                 activation_time_intervals=None,
                 maintenance_schedule=None,
                 user_message=None,
                 workflow_intervention_spec_vec=None):
        """Constructor for the MaintenanceModeConfigProto class"""

        # Initialize members of the class
        self.activation_time_intervals = activation_time_intervals
        self.maintenance_schedule = maintenance_schedule
        self.user_message = user_message
        self.workflow_intervention_spec_vec = workflow_intervention_spec_vec


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
        if dictionary.get("activationTimeIntervals") is not None:
            activation_time_intervals = list()
            for structure in dictionary.get('activationTimeIntervals'):
                activation_time_intervals.append(cohesity_management_sdk.models.time_range_usecs.TimeRangeUsecs.from_dictionary(structure))
        maintenance_schedule = cohesity_management_sdk.models.schedule_proto.ScheduleProto.from_dictionary(dictionary.get('maintenanceSchedule')) if dictionary.get('maintenanceSchedule') else None
        user_message = dictionary.get('userMessage')
        workflow_intervention_spec_vec = None
        if dictionary.get("workflowInterventionSpecVec") is not None:
            workflow_intervention_spec_vec = list()
            for structure in dictionary.get('workflowInterventionSpecVec'):
                workflow_intervention_spec_vec.append(cohesity_management_sdk.models.maintenance_mode_config_proto_workflow_intervention_spec.MaintenanceModeConfigProto_WorkflowInterventionSpec.from_dictionary(structure))

        # Return an object of this model
        return cls(activation_time_intervals,
                   maintenance_schedule,
                   user_message,
                   workflow_intervention_spec_vec)



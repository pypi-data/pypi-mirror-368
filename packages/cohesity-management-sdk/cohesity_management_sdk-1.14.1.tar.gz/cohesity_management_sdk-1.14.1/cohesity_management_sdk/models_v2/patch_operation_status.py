# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.patch_operation_service_unit_progress

class PatchOperationStatus(object):

    """Implementation of the 'Patch Operation Status.' model.

    Specifies the status of the current or the last patch operation.

    Attributes:
        in_progress (bool): Specifies whether a operation is in progress now.
        operation (string): Specifies the patch operation. It is either apply
            or revert patch operation.
        percentage (long|int): Specifies the percentage of completion of the
            current patch operation in progress or the last patch operation
            completed.
        time_remaining_seconds (long|int): Specifies the time remaining to
            complete the patch operation.
        time_taken_seconds (long|int): Specifies the time taken so far to
            complete the patch operation.
        services_progress (list of PatchOperationServiceUnitProgress):
            Specifies the details of patch operation services at each patch
            level.
        operation_message (string): Specifies a message about the patch
            operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "in_progress":'inProgress',
        "operation":'operation',
        "percentage":'percentage',
        "time_remaining_seconds":'timeRemainingSeconds',
        "time_taken_seconds":'timeTakenSeconds',
        "services_progress":'servicesProgress',
        "operation_message":'operationMessage'
    }

    def __init__(self,
                 in_progress=None,
                 operation=None,
                 percentage=None,
                 time_remaining_seconds=None,
                 time_taken_seconds=None,
                 services_progress=None,
                 operation_message=None):
        """Constructor for the PatchOperationStatus class"""

        # Initialize members of the class
        self.in_progress = in_progress
        self.operation = operation
        self.percentage = percentage
        self.time_remaining_seconds = time_remaining_seconds
        self.time_taken_seconds = time_taken_seconds
        self.services_progress = services_progress
        self.operation_message = operation_message


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
        in_progress = dictionary.get('inProgress')
        operation = dictionary.get('operation')
        percentage = dictionary.get('percentage')
        time_remaining_seconds = dictionary.get('timeRemainingSeconds')
        time_taken_seconds = dictionary.get('timeTakenSeconds')
        services_progress = None
        if dictionary.get("servicesProgress") is not None:
            services_progress = list()
            for structure in dictionary.get('servicesProgress'):
                services_progress.append(cohesity_management_sdk.models_v2.patch_operation_service_unit_progress.PatchOperationServiceUnitProgress.from_dictionary(structure))
        operation_message = dictionary.get('operationMessage')

        # Return an object of this model
        return cls(in_progress,
                   operation,
                   percentage,
                   time_remaining_seconds,
                   time_taken_seconds,
                   services_progress,
                   operation_message)



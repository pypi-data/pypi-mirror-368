# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.patch_operation_node_unit_progress

class PatchOperationServiceUnitProgress(object):

    """Implementation of the 'Patch Operation Service Unit Progress.' model.

    Specifies the progress of one patch operation for one service at one patch
    level.

    Attributes:
        service (string): Specifies the service which is patched.
        in_progress (bool): Specifies whether a operation is in progress for
            the service.
        percentage (long|int): Specifies the percentage of completion of the
            patch unit operation.
        time_remaining_seconds (long|int): Specifies the time remaining to
            complete the patch operation for the service.
        time_taken_seconds (long|int): Specifies the time taken so far in this
            patch unit operation for the service.
        nodes_progress (list of PatchOperationNodeUnitProgress): Specifies the
            details of patch operation for each service at each patch level.
        service_message (string): Specifies a message about the patch unit
            operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "service":'service',
        "in_progress":'inProgress',
        "percentage":'percentage',
        "time_remaining_seconds":'timeRemainingSeconds',
        "time_taken_seconds":'timeTakenSeconds',
        "nodes_progress":'nodesProgress',
        "service_message":'serviceMessage'
    }

    def __init__(self,
                 service=None,
                 in_progress=None,
                 percentage=None,
                 time_remaining_seconds=None,
                 time_taken_seconds=None,
                 nodes_progress=None,
                 service_message=None):
        """Constructor for the PatchOperationServiceUnitProgress class"""

        # Initialize members of the class
        self.service = service
        self.in_progress = in_progress
        self.percentage = percentage
        self.time_remaining_seconds = time_remaining_seconds
        self.time_taken_seconds = time_taken_seconds
        self.nodes_progress = nodes_progress
        self.service_message = service_message


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
        service = dictionary.get('service')
        in_progress = dictionary.get('inProgress')
        percentage = dictionary.get('percentage')
        time_remaining_seconds = dictionary.get('timeRemainingSeconds')
        time_taken_seconds = dictionary.get('timeTakenSeconds')
        nodes_progress = None
        if dictionary.get("nodesProgress") is not None:
            nodes_progress = list()
            for structure in dictionary.get('nodesProgress'):
                nodes_progress.append(cohesity_management_sdk.models_v2.patch_operation_node_unit_progress.PatchOperationNodeUnitProgress.from_dictionary(structure))
        service_message = dictionary.get('serviceMessage')

        # Return an object of this model
        return cls(service,
                   in_progress,
                   percentage,
                   time_remaining_seconds,
                   time_taken_seconds,
                   nodes_progress,
                   service_message)



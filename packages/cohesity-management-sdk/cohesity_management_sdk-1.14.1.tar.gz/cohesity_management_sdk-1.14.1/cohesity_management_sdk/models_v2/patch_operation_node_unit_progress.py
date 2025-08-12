# -*- coding: utf-8 -*-


class PatchOperationNodeUnitProgress(object):

    """Implementation of the 'Patch Operation Node Unit Progress.' model.

    Specifies the progress of the patch operation on a node.

    Attributes:
        node_ip (string): Specifies the IP address of the node.
        in_progress (bool): Specifies whether a operation is in progress on
            the node.
        patch_level_transition (string): Specifies the patch level transition
            of the patch operation. For Apply operation, patch level goes up
            for each operation. For Revert operation, patch level goes down.
            Patch level zero is the base level where no patch was applied.
        percentage (long|int): Specifies the percentage of completion of the
            patch operation on the node.
        time_taken_seconds (long|int): Specifies the time taken so far in this
            patch unit operation on the node.
        node_message (string): Specifies a message about the patch operation
            on the node.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_ip":'nodeIp',
        "in_progress":'inProgress',
        "patch_level_transition":'patchLevelTransition',
        "percentage":'percentage',
        "time_taken_seconds":'timeTakenSeconds',
        "node_message":'nodeMessage'
    }

    def __init__(self,
                 node_ip=None,
                 in_progress=None,
                 patch_level_transition=None,
                 percentage=None,
                 time_taken_seconds=None,
                 node_message=None):
        """Constructor for the PatchOperationNodeUnitProgress class"""

        # Initialize members of the class
        self.node_ip = node_ip
        self.in_progress = in_progress
        self.patch_level_transition = patch_level_transition
        self.percentage = percentage
        self.time_taken_seconds = time_taken_seconds
        self.node_message = node_message


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
        node_ip = dictionary.get('nodeIp')
        in_progress = dictionary.get('inProgress')
        patch_level_transition = dictionary.get('patchLevelTransition')
        percentage = dictionary.get('percentage')
        time_taken_seconds = dictionary.get('timeTakenSeconds')
        node_message = dictionary.get('nodeMessage')

        # Return an object of this model
        return cls(node_ip,
                   in_progress,
                   patch_level_transition,
                   percentage,
                   time_taken_seconds,
                   node_message)



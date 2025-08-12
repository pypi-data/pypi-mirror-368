# -*- coding: utf-8 -*-


class ExternalTargetInfo(object):

    """Implementation of the 'ExternalTargetInfo' model.

    Specifies the external target information if this is an archival
    snapshot.

    Attributes:
        target_id (long|int): Specifies the archival target ID.
        archival_task_id (string): Specifies the archival task id. This is a
            protection group UID which only applies when archival type is
            'Tape'.
        target_name (string): Specifies the archival target name.
        target_type (TargetType1Enum): Specifies the archival target type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_id":'targetId',
        "archival_task_id":'archivalTaskId',
        "target_name":'targetName',
        "target_type":'targetType'
    }

    def __init__(self,
                 target_id=None,
                 archival_task_id=None,
                 target_name=None,
                 target_type=None):
        """Constructor for the ExternalTargetInfo class"""

        # Initialize members of the class
        self.target_id = target_id
        self.archival_task_id = archival_task_id
        self.target_name = target_name
        self.target_type = target_type


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
        target_id = dictionary.get('targetId')
        archival_task_id = dictionary.get('archivalTaskId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')

        # Return an object of this model
        return cls(target_id,
                   archival_task_id,
                   target_name,
                   target_type)



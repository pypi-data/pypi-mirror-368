# -*- coding: utf-8 -*-


class RetrieveArchiveTask(object):

    """Implementation of the 'RetrieveArchiveTask' model.

    Specifies the persistent state of a retrieve of an archive task.

    Attributes:
        task_uid (string): Specifies the globally unique id for this retrieval of an archive
          task.
        uptier_expiry_times (list of long|int): Specifies how much time the retrieved entity is present in the
          hot-tiers.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "task_uid":'taskUid',
        "uptier_expiry_times":'uptierExpiryTimes'
    }

    def __init__(self,
                 task_uid=None,
                 uptier_expiry_times=None):
        """Constructor for the RetrieveArchiveTask class"""

        # Initialize members of the class
        self.task_uid = task_uid
        self.uptier_expiry_times = uptier_expiry_times


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
        task_uid = dictionary.get('taskUid')
        uptier_expiry_times = dictionary.get('uptierExpiryTimes')

        # Return an object of this model
        return cls(task_uid,
                   uptier_expiry_times)
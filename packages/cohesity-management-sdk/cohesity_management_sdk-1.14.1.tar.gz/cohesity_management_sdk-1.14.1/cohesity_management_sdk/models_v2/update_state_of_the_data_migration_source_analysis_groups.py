# -*- coding: utf-8 -*-


class UpdateStateOfTheDataMigrationSourceAnalysisGroups(object):

    """Implementation of the 'Update state of the Data Migration source analysis groups.' model.

    Specifies the parameters to perform an action on the Data Migration source
    analysis groups
    for the specified Sources.

    Attributes:
        action (Action4Enum): Specifies the action to be performed on all the
            specified Data Migration source analysis groups. 'Pause' 
            specifies to pause. 'Resume' specifies to resume.
        ids (list of long|int): Specifies a list of Data Migration source
            analysis groups ids for which the state should change.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "action":'action',
        "ids":'ids'
    }

    def __init__(self,
                 action=None,
                 ids=None):
        """Constructor for the UpdateStateOfTheDataMigrationSourceAnalysisGroups class"""

        # Initialize members of the class
        self.action = action
        self.ids = ids


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
        action = dictionary.get('action')
        ids = dictionary.get('ids')

        # Return an object of this model
        return cls(action,
                   ids)



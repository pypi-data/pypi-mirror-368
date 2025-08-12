# -*- coding: utf-8 -*-


class StandbyResoureParams(object):

    """Implementation of the 'Standby resoure Params.' model.

    Specifies the params for standby resource.

    Attributes:
        recovery_point_objective_secs (long|int): Specifies the recovery point
            objective time user expects for this standby resource.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_point_objective_secs":'recoveryPointObjectiveSecs'
    }

    def __init__(self,
                 recovery_point_objective_secs=None):
        """Constructor for the StandbyResoureParams class"""

        # Initialize members of the class
        self.recovery_point_objective_secs = recovery_point_objective_secs


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
        recovery_point_objective_secs = dictionary.get('recoveryPointObjectiveSecs')

        # Return an object of this model
        return cls(recovery_point_objective_secs)



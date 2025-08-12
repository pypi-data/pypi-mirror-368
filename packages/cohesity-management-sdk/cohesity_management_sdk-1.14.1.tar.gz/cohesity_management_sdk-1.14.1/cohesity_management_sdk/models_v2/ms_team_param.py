# -*- coding: utf-8 -*-


class MsTeamParam(object):

    """Implementation of the 'MsTeamParam' model.

    Specifies the parameters to recover a Microsoft 365 Team.

    Attributes:
        recover_entire_ms_team (bool): Specifies whether to recover the whole
            Microsoft 365 Team.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_entire_ms_team":'recoverEntireMsTeam'
    }

    def __init__(self,
                 recover_entire_ms_team=None):
        """Constructor for the MsTeamParam class"""

        # Initialize members of the class
        self.recover_entire_ms_team = recover_entire_ms_team


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
        recover_entire_ms_team = dictionary.get('recoverEntireMsTeam')

        # Return an object of this model
        return cls(recover_entire_ms_team)



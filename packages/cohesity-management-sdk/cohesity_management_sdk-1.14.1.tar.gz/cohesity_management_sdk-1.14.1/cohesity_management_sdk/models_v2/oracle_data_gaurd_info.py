# -*- coding: utf-8 -*-



class OracleDataGuardInfo(object):

    """Implementation of the 'OracleDataGuardInfo' model.

    Dataguard info about Oracle database.

    Attributes:
        role (RoleEnum1): Specifies the role of the Oracle DataGuard database.
        standby_type (StandbyEnum1): Specifies the type of the standby oracle database.
    """
    # Create a mapping from Model property names to API property names
    _names = {
        "role":'role',
        "standby_type":'standbyType'

    }

    def __init__(self,
                 role=None,
                 standby_type=None):
        """Constructor for the OracleDataGuardInfo class"""

        # Initialize members of the class
        self.role = role
        self.standby_type = standby_type


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
        role = dictionary.get('role')
        standby_type = dictionary.get('standbyType')

        # Return an object of this model
        return cls(role,
                   standby_type)
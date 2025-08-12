# -*- coding: utf-8 -*-


class RetentionUnits(object):

    """Implementation of the 'RetentionUnits' model.

    Retention Units.

    Attributes:
        retention_units (RetentionUnits1Enum): Specifies the retention unit.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "retention_units":'retentionUnits'
    }

    def __init__(self,
                 retention_units=None):
        """Constructor for the RetentionUnits class"""

        # Initialize members of the class
        self.retention_units = retention_units


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
        retention_units = dictionary.get('retentionUnits')

        # Return an object of this model
        return cls(retention_units)



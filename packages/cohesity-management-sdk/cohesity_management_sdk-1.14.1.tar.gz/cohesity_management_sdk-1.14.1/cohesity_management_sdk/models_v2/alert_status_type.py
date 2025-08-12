# -*- coding: utf-8 -*-


class AlertStatusType(object):

    """Implementation of the 'Alert Status type.' model.

    Alert Status type.

    Attributes:
        alert_status (AlertStatusEnum): Specifies Alert Status type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "alert_status":'alertStatus'
    }

    def __init__(self,
                 alert_status=None):
        """Constructor for the AlertStatusType class"""

        # Initialize members of the class
        self.alert_status = alert_status


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
        alert_status = dictionary.get('alertStatus')

        # Return an object of this model
        return cls(alert_status)



# -*- coding: utf-8 -*-


class ExtendedRetentionSchedule(object):

    """Implementation of the 'Extended Retention Schedule' model.

    Specifies a schedule frequency and schedule unit for Extended Retentions.

    Attributes:
        unit (Unit9Enum): Specifies the unit interval for retention of
            Snapshots. <br>'Runs' means that the Snapshot copy retained after
            the number of Protection Group Runs equals the number specified in
            the frequency. <br>'Hours' means that the Snapshot copy retained
            hourly at the frequency set in the frequency, for example if
            scheduleFrequency is 2, the copy occurs every 2 hours. <br>'Days'
            means that the Snapshot copy gets retained daily at the frequency
            set in the frequency. <br>'Weeks' means that the Snapshot copy is
            retained weekly at the frequency set in the frequency.
            <br>'Months' means that the Snapshot copy is retained monthly at
            the frequency set in the Frequency. <br>'Years' means that the
            Snapshot copy is retained yearly at the frequency set in the
            Frequency.
        frequency (int): Specifies a factor to multiply the unit by, to
            determine the retention schedule. For example if set to 2 and the
            unit is hourly, then Snapshots from the first eligible Job Run for
            every 2 hour period is retained.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "frequency":'frequency'
    }

    def __init__(self,
                 unit=None,
                 frequency=None):
        """Constructor for the ExtendedRetentionSchedule class"""

        # Initialize members of the class
        self.unit = unit
        self.frequency = frequency


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
        unit = dictionary.get('unit')
        frequency = dictionary.get('frequency')

        # Return an object of this model
        return cls(unit,
                   frequency)



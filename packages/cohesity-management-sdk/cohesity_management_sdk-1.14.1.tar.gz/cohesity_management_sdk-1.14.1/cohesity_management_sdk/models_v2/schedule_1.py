# -*- coding: utf-8 -*-


class Schedule1(object):

    """Implementation of the 'Schedule1' model.

    Specifies a schedule frequency and schedule unit for copying Snapshots to
    backup targets.

    Attributes:
        unit (UnitEnum): Specifies the frequency that Snapshots should be
            copied to the specified target. Used in combination with
            multiplier. <br>'Runs' means that the Snapshot copy occurs after
            the number of Protection Group Runs equals the number specified in
            the frequency. <br>'Hours' means that the Snapshot copy occurs
            hourly at the frequency set in the frequency, for example if
            scheduleFrequency is 2, the copy occurs every 2 hours. <br>'Days'
            means that the Snapshot copy occurs daily at the frequency set in
            the frequency. <br>'Weeks' means that the Snapshot copy occurs
            weekly at the frequency set in the frequency. <br>'Months' means
            that the Snapshot copy occurs monthly at the frequency set in the
            Frequency. <br>'Years' means that the Snapshot copy occurs yearly
            at the frequency set in the scheduleFrequency.
        frequency (int): Specifies a factor to multiply the unit by, to
            determine the copy schedule. For example if set to 2 and the unit
            is hourly, then Snapshots from the first eligible Job Run for
            every 2 hour period is copied.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "unit":'unit',
        "frequency":'frequency'
    }

    def __init__(self,
                 unit=None,
                 frequency=None):
        """Constructor for the Schedule1 class"""

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



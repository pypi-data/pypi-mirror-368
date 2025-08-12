# -*- coding: utf-8 -*-


class FilerLifecycleAgingPolicy(object):

    """Implementation of the 'FilerLifecycleAgingPolicy' model.

    Specifies the aging policy. Note: Both the fields days and dateInUsecs
      are mutually exclusive to each other.

    Attributes:
        aging_criteria (AgingCriteriaEnum): Specifies the criteria for aging
        date_in_usecs (long|int): Files that possess timestamps exceeding the specified value will
          be eligible for selection.
        days (long|int): Files that possess timestamps older than the specified value
          in days will be eligible for selection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aging_criteria":'agingCriteria',
        "date_in_usecs":'dateInUsecs',
        "days":'days'
    }

    def __init__(self,
                 aging_criteria=None,
                 date_in_usecs=None,
                 days=None):
        """Constructor for the FilerLifecycleAgingPolicy class"""

        # Initialize members of the class
        self.aging_criteria = aging_criteria
        self.date_in_usecs = date_in_usecs
        self.days = days


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
        aging_criteria = dictionary.get('agingCriteria')
        date_in_usecs = dictionary.get('dateInUsecs')
        days = dictionary.get('days')

        # Return an object of this model
        return cls(aging_criteria,
                   date_in_usecs,
                   days)
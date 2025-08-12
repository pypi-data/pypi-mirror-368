# -*- coding: utf-8 -*-


class RunFilterValues(object):

    """Implementation of the 'Run Filter Values.' model.

    Run Filter Values.

    Attributes:
        run_filter_values (RunFilterValues1Enum): Specifies Run Filter Value.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "run_filter_values":'runFilterValues'
    }

    def __init__(self,
                 run_filter_values=None):
        """Constructor for the RunFilterValues class"""

        # Initialize members of the class
        self.run_filter_values = run_filter_values


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
        run_filter_values = dictionary.get('runFilterValues')

        # Return an object of this model
        return cls(run_filter_values)



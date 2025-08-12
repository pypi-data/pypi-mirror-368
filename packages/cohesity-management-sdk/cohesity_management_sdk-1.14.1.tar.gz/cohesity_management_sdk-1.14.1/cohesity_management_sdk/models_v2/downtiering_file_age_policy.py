# -*- coding: utf-8 -*-


class DowntieringFileAgePolicy(object):

    """Implementation of the 'DowntieringFileAgePolicy' model.

    Specifies the file's selection rule by file age for down tiering data
    tiering task eg.
    1. select files older than 10 days.
    2. select files last accessed 2 weeks ago.
    3. select files last modified 1 month ago.

    Attributes:
        condition (Condition1Enum): Specifies the condition for the file age.
        age_msecs (long|int): Specifies the number of msecs used for file
            selection.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "condition":'condition',
        "age_msecs":'ageMsecs'
    }

    def __init__(self,
                 condition=None,
                 age_msecs=None):
        """Constructor for the DowntieringFileAgePolicy class"""

        # Initialize members of the class
        self.condition = condition
        self.age_msecs = age_msecs


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
        condition = dictionary.get('condition')
        age_msecs = dictionary.get('ageMsecs')

        # Return an object of this model
        return cls(condition,
                   age_msecs)



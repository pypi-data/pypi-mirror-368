# -*- coding: utf-8 -*-


class UptieringFileAgePolicy(object):

    """Implementation of the 'UptieringFileAgePolicy' model.

    Specifies the file's selection rule by file age for up tiering data
    tiering task eg.
    1. select files last accessed 2 weeks ago.
    2. select files last modified 1 month ago.

    Attributes:
        condition (Condition2Enum): Specifies the condition for the file age.
        age_msecs (long|int): Specifies the number of msecs used for file
            selection.
        num_file_access (int): Specifies number of file access in last
            ageMsecs.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "condition":'condition',
        "age_msecs":'ageMsecs',
        "num_file_access":'numFileAccess'
    }

    def __init__(self,
                 condition=None,
                 age_msecs=None,
                 num_file_access=None):
        """Constructor for the UptieringFileAgePolicy class"""

        # Initialize members of the class
        self.condition = condition
        self.age_msecs = age_msecs
        self.num_file_access = num_file_access


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
        num_file_access = dictionary.get('numFileAccess')

        # Return an object of this model
        return cls(condition,
                   age_msecs,
                   num_file_access)



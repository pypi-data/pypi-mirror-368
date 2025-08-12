# -*- coding: utf-8 -*-


class SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataTieringGroups(object):

    """Implementation of the 'Specifies the summary of the state updation for the multiple data
tiering groups.' model.

    TODO: type model description here.

    Attributes:
        failed_ids (list of string): Specifies a list of data tiering groups
            ids for which updation of state failed.
        successful_ids (list of string): Specifies a list of data tiering
            groups ids for which updation of state was successful.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "failed_ids":'failedIds',
        "successful_ids":'successfulIds'
    }

    def __init__(self,
                 failed_ids=None,
                 successful_ids=None):
        """Constructor for the SpecifiesTheSummaryOfTheStateUpdationForTheMultipleDataTieringGroups class"""

        # Initialize members of the class
        self.failed_ids = failed_ids
        self.successful_ids = successful_ids


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
        failed_ids = dictionary.get('failedIds')
        successful_ids = dictionary.get('successfulIds')

        # Return an object of this model
        return cls(failed_ids,
                   successful_ids)



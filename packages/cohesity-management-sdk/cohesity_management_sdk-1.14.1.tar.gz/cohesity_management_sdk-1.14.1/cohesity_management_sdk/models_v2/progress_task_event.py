# -*- coding: utf-8 -*-


class ProgressTaskEvent(object):

    """Implementation of the 'ProgressTaskEvent' model.

    Specifies the details about the various events which are created during
    the execution of Progress Task.

    Attributes:
        message (string): Specifies the log message describing the current
            event.
        occured_at_usecs (long|int): Specifies the time of the event occurance
            in Unix epoch Timestamp(in microseconds).

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "message":'message',
        "occured_at_usecs":'occuredAtUsecs'
    }

    def __init__(self,
                 message=None,
                 occured_at_usecs=None):
        """Constructor for the ProgressTaskEvent class"""

        # Initialize members of the class
        self.message = message
        self.occured_at_usecs = occured_at_usecs


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
        message = dictionary.get('message')
        occured_at_usecs = dictionary.get('occuredAtUsecs')

        # Return an object of this model
        return cls(message,
                   occured_at_usecs)



# -*- coding: utf-8 -*-


class RigelClaimLog(object):

    """Implementation of the 'Rigel Claim Log.' model.

    Specifies an event during Rigel claim..

    Attributes:
        time_stamp (long|int): Specifies the time stamp in microseconds of the
            event.
        message (string): Specifies the message of this event.
        mtype (string): Specifies the severity of the event.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "time_stamp":'timeStamp',
        "message":'message',
        "mtype":'type'
    }

    def __init__(self,
                 time_stamp=None,
                 message=None,
                 mtype=None):
        """Constructor for the RigelClaimLog class"""

        # Initialize members of the class
        self.time_stamp = time_stamp
        self.message = message
        self.mtype = mtype


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
        time_stamp = dictionary.get('timeStamp')
        message = dictionary.get('message')
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(time_stamp,
                   message,
                   mtype)



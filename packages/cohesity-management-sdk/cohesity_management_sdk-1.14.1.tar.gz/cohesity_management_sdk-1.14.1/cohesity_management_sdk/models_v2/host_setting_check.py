# -*- coding: utf-8 -*-


class HostSettingCheck(object):

    """Implementation of the 'HostSettingCheck' model.

    Specifies the host checking details.

    Attributes:
        mtype (Type1Enum): Specifies the type of host checking that was
            performed.
        result (ResultEnum): Specifies the result of host checking performed
            by agent.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "mtype":'type',
        "result":'result'
    }

    def __init__(self,
                 mtype=None,
                 result=None):
        """Constructor for the HostSettingCheck class"""

        # Initialize members of the class
        self.mtype = mtype
        self.result = result


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
        mtype = dictionary.get('type')
        result = dictionary.get('result')

        # Return an object of this model
        return cls(mtype,
                   result)



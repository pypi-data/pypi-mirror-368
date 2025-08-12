# -*- coding: utf-8 -*-


class VCDStorageProfileParams(object):

    """Implementation of the 'VCD Storage Profile Params' model.

    Specifies the parameters of a VCD storage profile.

    Attributes:
        vcd_uuid (string): Specifies the UUID assigned by the VCD to the
            storage profile.
        name (string): Specifies the name of the storage profile.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vcd_uuid":'vcdUuid',
        "name":'name'
    }

    def __init__(self,
                 vcd_uuid=None,
                 name=None):
        """Constructor for the VCDStorageProfileParams class"""

        # Initialize members of the class
        self.vcd_uuid = vcd_uuid
        self.name = name


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
        vcd_uuid = dictionary.get('vcdUuid')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(vcd_uuid,
                   name)



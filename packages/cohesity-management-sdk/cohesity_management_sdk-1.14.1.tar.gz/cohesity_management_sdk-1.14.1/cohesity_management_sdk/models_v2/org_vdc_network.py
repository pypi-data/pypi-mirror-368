# -*- coding: utf-8 -*-


class OrgVDCNetwork(object):

    """Implementation of the 'OrgVDCNetwork' model.

    Specifies a VDC Organization Network.

    Attributes:
        vcd_uuid (string): Specifies the UUID of network associated with the
            Virtual Cloud director.
        name (string): Specifies the name of the catalog.
        v_center_uuid (string): Specifies the UUID of network associated with
            the Vcenter.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "vcd_uuid":'vcdUuid',
        "name":'name',
        "v_center_uuid":'vCenterUuid'
    }

    def __init__(self,
                 vcd_uuid=None,
                 name=None,
                 v_center_uuid=None):
        """Constructor for the OrgVDCNetwork class"""

        # Initialize members of the class
        self.vcd_uuid = vcd_uuid
        self.name = name
        self.v_center_uuid = v_center_uuid


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
        v_center_uuid = dictionary.get('vCenterUuid')

        # Return an object of this model
        return cls(vcd_uuid,
                   name,
                   v_center_uuid)



# -*- coding: utf-8 -*-

class SmbActiveOpen(object):

    """Implementation of the 'SmbActiveOpen' model.

    Specifies an active open of an SMB file, its access and sharing
    information.

    Attributes:
        open_id (long|int): Specifies the id of the active open.
        access_info_list (AccessInfoListEnum): Specifies the File Access
            Type. 
        access_privilege (AccessPrivilegeEnum): Specifies whether access
            privilege of others if they're allowed to read/write/delete.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "open_id":'openId',
        "access_info_list":'accessInfoList',
        "access_privilege":'accessPrivilege'
    }

    def __init__(self,
                 open_id=None,
                 access_info_list=None,
                 access_privilege=None):
        """Constructor for the SmbActiveOpen class"""

        # Initialize members of the class
        self.open_id = open_id
        self.access_info_list = access_info_list
        self.access_privilege = access_privilege


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
        open_id = dictionary.get('openId')
        access_info_list = dictionary.get('accessInfoList')
        access_privilege = dictionary.get('accessPrivilege')

        # Return an object of this model
        return cls(open_id,
                   access_info_list,
                   access_privilege)



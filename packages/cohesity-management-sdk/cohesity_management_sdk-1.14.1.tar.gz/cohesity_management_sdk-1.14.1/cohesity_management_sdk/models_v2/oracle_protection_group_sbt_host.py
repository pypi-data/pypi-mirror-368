# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_vlan_info

class OracleProtectionGroupSBTHost(object):

    """Implementation of the 'Oracle Protection Group SBT Host' model.

    Specifies details about capturing Oracle SBT host info.

    Attributes:
        sbt_library_path (string): Specifies the path of sbt library.
        view_fs_path (string): Specifies the Cohesity view path.
        vip_list (list of string): Specifies the list of Cohesity primary
            VIPs.
        vlan_info_list (list of OracleProtectionGroupVlanInfo): Specifies the
            Vlan information for Cohesity cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "sbt_library_path":'sbtLibraryPath',
        "view_fs_path":'viewFsPath',
        "vip_list":'vipList',
        "vlan_info_list":'vlanInfoList'
    }

    def __init__(self,
                 sbt_library_path=None,
                 view_fs_path=None,
                 vip_list=None,
                 vlan_info_list=None):
        """Constructor for the OracleProtectionGroupSBTHost class"""

        # Initialize members of the class
        self.sbt_library_path = sbt_library_path
        self.view_fs_path = view_fs_path
        self.vip_list = vip_list
        self.vlan_info_list = vlan_info_list


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
        sbt_library_path = dictionary.get('sbtLibraryPath')
        view_fs_path = dictionary.get('viewFsPath')
        vip_list = dictionary.get('vipList')
        vlan_info_list = None
        if dictionary.get("vlanInfoList") is not None:
            vlan_info_list = list()
            for structure in dictionary.get('vlanInfoList'):
                vlan_info_list.append(cohesity_management_sdk.models_v2.oracle_protection_group_vlan_info.OracleProtectionGroupVlanInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(sbt_library_path,
                   view_fs_path,
                   vip_list,
                   vlan_info_list)



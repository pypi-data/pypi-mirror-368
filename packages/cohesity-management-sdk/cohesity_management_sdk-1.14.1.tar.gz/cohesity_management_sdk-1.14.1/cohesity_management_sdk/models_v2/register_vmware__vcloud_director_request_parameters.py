# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_v_center_credential_info

class RegisterVmwareVcloudDirectorRequestParameters(object):

    """Implementation of the 'Register VMware vCloud director request parameters.' model.

    Specifies parameters to register VMware vCloud director.

    Attributes:
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the host.
        description (string): Specifies the description of the source being
            registered.
        vcenter_credential_info_list (list of VmwareVCenterCredentialInfo):
            Specifies the credentials information for all the vcenters in
            vcloud director.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password',
        "endpoint":'endpoint',
        "description":'description',
        "vcenter_credential_info_list":'vcenterCredentialInfoList'
    }

    def __init__(self,
                 username=None,
                 password=None,
                 endpoint=None,
                 description=None,
                 vcenter_credential_info_list=None):
        """Constructor for the RegisterVmwareVcloudDirectorRequestParameters class"""

        # Initialize members of the class
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.description = description
        self.vcenter_credential_info_list = vcenter_credential_info_list


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
        username = dictionary.get('username')
        password = dictionary.get('password')
        endpoint = dictionary.get('endpoint')
        description = dictionary.get('description')
        vcenter_credential_info_list = None
        if dictionary.get("vcenterCredentialInfoList") is not None:
            vcenter_credential_info_list = list()
            for structure in dictionary.get('vcenterCredentialInfoList'):
                vcenter_credential_info_list.append(cohesity_management_sdk.models_v2.vmware_v_center_credential_info.VmwareVCenterCredentialInfo.from_dictionary(structure))

        # Return an object of this model
        return cls(username,
                   password,
                   endpoint,
                   description,
                   vcenter_credential_info_list)



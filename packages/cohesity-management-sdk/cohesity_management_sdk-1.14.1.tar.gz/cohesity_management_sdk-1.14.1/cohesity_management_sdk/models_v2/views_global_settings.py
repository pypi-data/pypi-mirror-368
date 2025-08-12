# -*- coding: utf-8 -*-


class ViewsGlobalSettings(object):

    """Implementation of the 'ViewsGlobalSettings' model.

    Specifies the Global Settings for SmartFiles.

    Attributes:
        enable_remote_views_gui_visibility (bool): Specifies the visibility of Remote
           Cohesity Views on Cohesity GUI.
        enable_remote_views_visibility (bool): Specifies the visibility of Remote Cohesity Views for external
          clients.
        enable_smb_auth (bool): Specifies if SMB Authentication should be enabled.
        enable_smb_multi_channel (bool): Specifies if SMB Multi-Channel should be enabled.
        s3_virtual_hosted_domain_names (list of string): Specifies the list of domain names for S3 Virtual Hosted Style
          Paths. If set, all the Cohesity S3 Views in the cluster can be accessed
          using any of the specified domain names.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "enable_remote_views_gui_visibility":'enableRemoteViewsGuiVisibility',
        "enable_remote_views_visibility":'enableRemoteViewsVisibility',
        "enable_smb_auth":'enableSmbAuth',
        "enable_smb_multi_channel":'enableSmbMultiChannel',
        "s3_virtual_hosted_domain_names":'s3VirtualHostedDomainNames'
    }

    def __init__(self,
                 enable_remote_views_gui_visibility=None,
                 enable_remote_views_visibility=None,
                 enable_smb_auth=None,
                 enable_smb_multi_channel=None,
                 s3_virtual_hosted_domain_names=None
                 ):
        """Constructor for the ViewsGlobalSettings class"""

        # Initialize members of the class
        self.enable_remote_views_gui_visibility = enable_remote_views_gui_visibility
        self.enable_remote_views_visibility = enable_remote_views_visibility
        self.enable_smb_auth = enable_smb_auth
        self.enable_smb_multi_channel = enable_smb_multi_channel
        self.s3_virtual_hosted_domain_names = s3_virtual_hosted_domain_names


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
        enable_remote_views_gui_visibility = dictionary.get('enableRemoteViewsGuiVisibility')
        enable_remote_views_visibility = dictionary.get('enableRemoteViewsVisibility')
        enable_smb_auth = dictionary.get('enableSmbAuth')
        enable_smb_multi_channel = dictionary.get('enableSmbMultiChannel')
        s3_virtual_hosted_domain_names = dictionary.get('s3VirtualHostedDomainNames')


        # Return an object of this model
        return cls(enable_remote_views_gui_visibility,
                   enable_remote_views_visibility,
                   enable_smb_auth,
                   enable_smb_multi_channel,
                   s3_virtual_hosted_domain_names)
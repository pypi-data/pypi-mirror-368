# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.credentials_1
import cohesity_management_sdk.models_v2.view_params
import cohesity_management_sdk.models_v2.key_value_pair

class RegisterUniversalDataAdapterSourceRegistrationRequestParameters(object):

    """Implementation of the 'Register Universal Data Adapter source registration request parameters.' model.

    Specifies parameters to register a Universal Data Adapter source.

    Attributes:
        source_type (SourceType2Enum): Specifies the source type for Universal
            Data Adapter source.
        os_type (string): Specifies the operating system type of the object.
            Currently only Linux is supported.
        hosts (list of string): Specifies the IPs/hostnames for the nodes
            forming the Universal Data Adapter source cluster.
        credentials (Credentials1): Specifies credentials to access the
            Universal Data Adapter source. For e.g.: To perform backup and
            recovery tasks with Oracle Recovery Manager (RMAN), specify
            credentials for a user having 'SYSDBA' or 'SYSBACKUP'
            administrative privilege.
        script_dir (string): Specifies the absolute path of scripts used to
            interact with the Universal Data Adapter source.
        mount_view (bool): Specifies if SMB/NFS view mounting should be
            enabled. If set to true, configuration for the mounted view can be
            optionally specified inside the viewParams. Default value is
            false.
        view_params (ViewParams): Specifies optional configuration parameters
            for the mounted view.
        source_registration_args (string): Specifies custom arguments to be
            supplied to the source registration scripts.
        source_registration_arguments (list of KeyValuePair): Specifies the map of custom arguments to be supplied to the source
          registration scripts.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_type":'sourceType',
        "os_type":'osType',
        "hosts":'hosts',
        "script_dir":'scriptDir',
        "credentials":'credentials',
        "mount_view":'mountView',
        "view_params":'viewParams',
        "source_registration_args":'sourceRegistrationArgs',
        "source_registration_arguments":'sourceRegistrationArguments'
    }

    def __init__(self,
                 source_type=None,
                 os_type='kLinux',
                 hosts=None,
                 script_dir=None,
                 credentials=None,
                 mount_view=None,
                 view_params=None,
                 source_registration_args=None,
                 source_registration_arguments=None):
        """Constructor for the RegisterUniversalDataAdapterSourceRegistrationRequestParameters class"""

        # Initialize members of the class
        self.source_type = source_type
        self.os_type = os_type
        self.hosts = hosts
        self.credentials = credentials
        self.script_dir = script_dir
        self.mount_view = mount_view
        self.view_params = view_params
        self.source_registration_args = source_registration_args
        self.source_registration_arguments = source_registration_arguments


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
        source_type = dictionary.get('sourceType')
        os_type = dictionary.get("osType") if dictionary.get("osType") else 'kLinux'
        hosts = dictionary.get('hosts')
        script_dir = dictionary.get('scriptDir')
        credentials = cohesity_management_sdk.models_v2.credentials_1.Credentials1.from_dictionary(dictionary.get('credentials')) if dictionary.get('credentials') else None
        mount_view = dictionary.get('mountView')
        view_params = cohesity_management_sdk.models_v2.view_params.ViewParams.from_dictionary(dictionary.get('viewParams')) if dictionary.get('viewParams') else None
        source_registration_args = dictionary.get('sourceRegistrationArgs')
        source_registration_arguments = None
        if dictionary.get('sourceRegistrationArguments') is not None:
            source_registration_arguments =  list()
            for structure in dictionary.get('sourceRegistrationArguments'):
                source_registration_arguments.append(cohesity_management_sdk.models_v2.key_value_pair.KeyValuePair.from_dictionary(structure))

        # Return an object of this model
        return cls(source_type,
                   os_type,
                   hosts,
                   script_dir,
                   credentials,
                   mount_view,
                   view_params,
                   source_registration_args,
                   source_registration_arguments)
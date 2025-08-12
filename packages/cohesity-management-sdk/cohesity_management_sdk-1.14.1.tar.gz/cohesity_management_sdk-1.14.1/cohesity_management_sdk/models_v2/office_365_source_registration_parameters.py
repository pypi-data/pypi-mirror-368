# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.credentials
import cohesity_management_sdk.models_v2.office_365_azure_application_credentials
import cohesity_management_sdk.models_v2.office_365_objects_discovery_parameters

class Office365SourceRegistrationParameters(object):

    """Implementation of the 'Office365SourceRegistrationParameters' model.

    Specifies the paramaters to register an office-365 source.

    Attributes:
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the host.
        description (string): Specifies the description of the source being
            registered.
        o_365_objects_discovery_params (Office365ObjectsDiscoveryparameters): Specifies the parameters used for selectively discovering
            the office 365 objects during source registration or refresh. Example:
            o365ObjectsDiscoveryParams: { discoverableObjectTypeList:{[''kUsers'',
            ''kSites'', ''kGroups'']}, usersDiscoveryParams:{discoverUsersWithMailbox:true,
            discoverUsersWithOnedrive:false} }
        office_365_app_credentials_list (list of Office365AzureApplicationCredentials): Specifies a list of office365 azure application credentials
            needed to authenticate & authorize users for Office 365.
        office_365_region (Office365RegionEnum): Specifies the region where Office 365 Exchange environment
            is.
        office_365_service_account_credentials_list (list of Credentials): Specifies the list of Office365 service account credentials
            which can be used for Mailbox Backups.
        proxy_host_source_id_list (list of long|int): Specifies the list of the protection source id of the windows
            physical host which will be used during the protection and recovery of
            the sites that belong to a office365 domain.
        use_existing_credentials (bool): Specifies whether to use existing Office365 credentials like
            password and client secret for app id's. This parameter is only valid
            in the case of updating the registered source.
        use_o_auth_for_exchange_online (bool): Specifies whether OAuth should be used for authentication in
            case of Exchange Online.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password',
        "endpoint":'endpoint',
        "description":'description',
        "o_365_objects_discovery_params":'o365ObjectsDiscoveryParams',
        "office_365_app_credentials_list":'office365AppCredentialsList',
        "office_365_region":'office365Region',
        "office_365_service_account_credentials_list":'office365ServiceAccountCredentialsList',
        "proxy_host_source_id_list":'proxyHostSourceIdList',
        "use_existing_credentials":'useExistingCredentials',
        "use_o_auth_for_exchange_online":'useOAuthForExchangeOnline'
    }

    def __init__(self,
                 username=None,
                 password=None,
                 endpoint=None,
                 description=None,
                 o_365_objects_discovery_params=None,
                 office_365_app_credentials_list=None,
                 office_365_region=None,
                 office_365_service_account_credentials_list=None,
                 proxy_host_source_id_list=None,
                 use_existing_credentials=None,
                 use_o_auth_for_exchange_online=None):
        """Constructor for the Office365SourceRegistrationParameters class"""

        # Initialize members of the class
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.description = description
        self.o_365_objects_discovery_params = o_365_objects_discovery_params
        self.office_365_app_credentials_list = office_365_app_credentials_list
        self.office_365_region = office_365_region
        self.office_365_service_account_credentials_list = office_365_service_account_credentials_list
        self.proxy_host_source_id_list = proxy_host_source_id_list
        self.use_existing_credentials = use_existing_credentials
        self.use_o_auth_for_exchange_online = use_o_auth_for_exchange_online


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
        o_365_objects_discovery_params = dictionary.get('o365ObjectsDiscoveryParams')
        office_365_app_credentials_list = None
        if dictionary.get('office365AppCredentialsList') is not None:
            office_365_app_credentials_list = list()
            for structure in dictionary.get('office365AppCredentialsList'):
                office_365_app_credentials_list.append(cohesity_management_sdk.models_v2.office_365_azure_application_credentials.Office365AzureApplicationCredentials.from_dictionary(structure))
        office_365_region = dictionary.get('office365Region')
        office_365_service_account_credentials_list = None
        if dictionary.get('office365ServiceAccountCredentialsList') is not None:
            office_365_service_account_credentials_list = list()
            for structure in dictionary.get('office365ServiceAccountCredentialsList'):
                office_365_service_account_credentials_list.append(cohesity_management_sdk.models_v2.credentials.Credentials.from_dictionary(structure))
        proxy_host_source_id_list = dictionary.get('proxyHostSourceIdList')
        use_existing_credentials = dictionary.get('useExistingCredentials')
        use_o_auth_for_exchange_online = dictionary.get('useOAuthForExchangeOnline')

        # Return an object of this model
        return cls(username,
                   password,
                   endpoint,
                   description,
                   o_365_objects_discovery_params,
                   office_365_app_credentials_list,
                   office_365_region,
                   office_365_service_account_credentials_list,
                   proxy_host_source_id_list,
                   use_existing_credentials,
                   use_o_auth_for_exchange_online)
# -*- coding: utf-8 -*-


class RegisterSFDCSourceRequestParameters(object):

    """Implementation of the 'Register SFDC source request parameters.' model.

    Specifies parameters to register an SFDC Protection Source.

    Attributes:
        auth_token (string): Specifies the token that will be used for fetching oAuth tokens
          from salesforce.
        callback_url (string): Specifies the URL added in the connected apps Callback URL field.
          You can find this URL on the connected apps Manage Connected Apps page or
          from the connected apps definition. This value must be URL encoded.
        concurrent_api_requests_limit (long|int): Specifies the maximum number of concurrent API requests allowed
          for salesforce.
        consumer_key (string): Specifies Consumer key from the connected app in SFDC.
        consumer_secret (string): Specifies Consumer secret from the connected app in SFDC.
        daily_api_limit (long|int): Specifies the maximum number of daily API requests allowed for
          salesforce.
        endpoint (string): Specifies the SFDC endpoint URL.
        endpoint_type (EndpointTypeEnum): SFDC Endpoint type.
        metadata_endpoint_url (string): Specifies the url to access salesforce metadata requests.
        password (string): Specifies the password to access salesforce.
        soap_endpoint_url (string): Specifies the url to access salesforce soap requests.
        username (string): Specifies the username to access salesforce.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "auth_token":'authToken',
        "callback_url":'callbackUrl',
        "concurrent_api_requests_limit":'concurrentApiRequestsLimit',
        "consumer_key":'consumerKey',
        "consumer_secret":'consumerSecret',
        "daily_api_limit":'dailyApiLimit',
        "endpoint":'endpoint',
        "endpoint_type":'endpointType',
        "metadata_endpoint_url":'metadataEndpointUrl',
        "password":'password',
        "soap_endpoint_url":'soapEndpointUrl',
        "username":'username'
    }

    def __init__(self,
                 auth_token=None,
                 callback_url=None,
                 concurrent_api_requests_limit=None,
                 consumer_key=None,
                 consumer_secret=None,
                 daily_api_limit=None,
                 endpoint=None,
                 endpoint_type=None,
                 metadata_endpoint_url=None,
                 password=None,
                 soap_endpoint_url=None,
                 username=None):
        """Constructor for the RegisterSFDCSourceRequestParameters class"""

        # Initialize members of the class
        self.auth_token = auth_token
        self.callback_url = callback_url
        self.concurrent_api_requests_limit = concurrent_api_requests_limit
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.daily_api_limit = daily_api_limit
        self.endpoint = endpoint
        self.endpoint_type = endpoint_type
        self.metadata_endpoint_url = metadata_endpoint_url
        self.password = password
        self.soap_endpoint_url = soap_endpoint_url
        self.username = username


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
        auth_token = dictionary.get('authToken')
        callback_url = dictionary.get('callbackUrl')
        concurrent_api_requests_limit = dictionary.get('concurrentApiRequestsLimit')
        consumer_key = dictionary.get('consumerKey')
        consumer_secret = dictionary.get('consumerSecret')
        daily_api_limit = dictionary.get('dailyApiLimit')
        endpoint = dictionary.get('endpoint')
        endpoint_type = dictionary.get('endpointType')
        metadata_endpoint_url = dictionary.get('metadataEndpointUrl')
        password = dictionary.get('password')
        soap_endpoint_url = dictionary.get('soapEndpointUrl')
        username = dictionary.get('username')

        # Return an object of this model
        return cls(auth_token,
                   callback_url,
                   concurrent_api_requests_limit,
                   consumer_key,
                   consumer_secret,
                   daily_api_limit,
                   endpoint,
                   endpoint_type,
                   metadata_endpoint_url,
                   password,
                   soap_endpoint_url,
                   username)
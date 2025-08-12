# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

class AuthMethodAzureCloudCredentialsEnum(object):

    """Implementation of the 'AuthMethodAzureCloudCredentials' enum.
    Specifies the auth method used for the request
    'kAzureAuthNone' indicates no authentication.
    'kAzureClientSecret' indicates a client authentication.
    'kAzureManagedIdentity' indicates a Azure based authentication.
    'kUseHelios' indicates a Helios authentication.

    Attributes:
        KAZUREAUTHNONE: TODO: type description here.
        KAZURECLIENTSECRET: TODO: type description here.
        KAZUREMANAGEDIDENTITY: TODO: type description here.
        KUSEHELIOS: TODO: type description here.

    """

    KAZUREAUTHNONE = 'kAzureAuthNone'

    KAZURECLIENTSECRET = 'kAzureClientSecret'

    KAZUREMANAGEDIDENTITY = 'kAzureManagedIdentity'

    KUSEHELIOS = 'kUseHelios'

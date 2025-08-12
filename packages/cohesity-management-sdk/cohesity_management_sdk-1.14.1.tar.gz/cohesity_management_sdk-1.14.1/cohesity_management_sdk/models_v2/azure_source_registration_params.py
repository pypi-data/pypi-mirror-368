# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.azure_application_credentials
import cohesity_management_sdk.models_v2.azure_subscription

class AzureSourceRegistrationParams(object):

    """Implementation of the 'AzureSourceRegistrationParams' model.

    Specifies the paramaters to register an Azure source.

    Attributes:
        application_credentials (list of AzureApplicationCredentials): Specifies the credentials for a list of applications from azure
          active directory.
        azure_tenant_id (string): Specifies Tenant Id of the active directory of Azure account.
          Accepts both Azure tanant Id and tenant domain name.
        registration_level (RegistrationLevelEnum): Specifies whether the registration is at tenant level or subscription
          level.
        registration_workflow (RegistrationWorkflowEnum): Specifies whether the type of registration is express or manual.
        subscription_details (list of AzureSubscription): Specifies the list subscription ids to be registered.
        use_cases (UseCasesEnum): The use cases for which the source is to be registered.
        """

    # Create a mapping from Model property names to API property names
    _names = {
        "application_credentials":'applicationCredentials',
        "azure_tenant_id":'azureTenantId',
        "registration_level":'registrationLevel',
        "registration_workflow": 'registrationWorkflow',
        "subscription_details": 'subscriptionDetails',
        "use_cases": 'useCases'
    }

    def __init__(self,
                 application_credentials=None,
                 azure_tenant_id=None,
                 registration_level=None,
                 registration_workflow=None,
                 subscription_details=None,
                 use_cases=None
                 ):
        """Constructor for the AzureSourceRegistrationParams class"""

        # Initialize members of the class
        self.application_credentials = application_credentials
        self.azure_tenant_id = azure_tenant_id
        self.registration_level = registration_level
        self.registration_workflow = registration_workflow
        self.subscription_details = subscription_details
        self.use_cases = use_cases

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
        application_credentials = None
        if dictionary.get('applicationCredentials') is not None:
            application_credentials = list()
            for structure in dictionary.get('applicationCredentials'):
                application_credentials.append(cohesity_management_sdk.models_v2.azure_application_credentials.AzureApplicationCredentials.from_dictionary(structure))
        azure_tenant_id = dictionary.get('azureTenantId')
        registration_level = dictionary.get('registrationLevel')
        registration_workflow = dictionary.get('registrationWorkflow')
        subscription_details = None
        if dictionary.get('subscriptionDetails') is not None:
            subscription_details = list()
            for structure in dictionary.get('subscriptionDetails'):
                subscription_details.append(cohesity_management_sdk.models_v2.azure_subscription.AzureSubscription.from_dictionary(structure))
        use_cases = dictionary.get('useCases')




        # Return an object of this model
        return cls(application_credentials,
                   azure_tenant_id,
                   registration_level,
                   registration_workflow,
                   subscription_details,
                   use_cases)
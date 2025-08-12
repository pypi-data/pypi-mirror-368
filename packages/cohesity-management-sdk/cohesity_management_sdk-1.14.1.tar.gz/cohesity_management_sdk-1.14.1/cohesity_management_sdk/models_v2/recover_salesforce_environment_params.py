# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.recover_salesforce_object_params
import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params

class RecoverSalesforceEnvironmentParams(object):
    """Implementation of the 'RecoverSalesforceParams' model.

    Specifies the recovery options specific to Salesforce environment.

    Attributes:
        continue_on_error (bool): Specifies whether to continue recovering other salesforce objects if one of Object failed to recover. Default value is false.
        objects (CommonRecoverObjectSnapshotParams): Specifies the list of recover Object parameters.
        recover_sfdc_object_params (RecoverSalesforceObjectParams): Specifies the parameters to recover Salesforce objects.
        recover_to (long|int): Specifies the id of registered source where the objects are to be recovered. If this is not specified, the recovery job will recover to the original location.
        recovery_action (string): Specifies the type of recover action to be performed.
    """

    _names = {
        "continue_on_error":"continueOnError",
        "objects":"objects",
        "recover_sfdc_object_params":"recoverSfdcObjectParams",
        "recover_to":"recoverTo",
        "recovery_action":"recoveryAction",
    }

    def __init__(self,
                 continue_on_error=None,
                 objects=None,
                 recover_sfdc_object_params=None,
                 recover_to=None,
                 recovery_action=None):
        """Constructor for the RecoverSalesforceParams class"""

        self.continue_on_error = continue_on_error
        self.objects = objects
        self.recover_sfdc_object_params = recover_sfdc_object_params
        self.recover_to = recover_to
        self.recovery_action = recovery_action


    @classmethod
    def from_dictionary(cls, dictionary):
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

        continue_on_error = dictionary.get('continueOnError')
        objects = None
        if dictionary.get('objects') is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_sfdc_object_params = cohesity_management_sdk.models_v2.recover_salesforce_object_params.RecoverSalesforceObjectParams.from_dictionary(dictionary.get('recoverSfdcObjectParams')) if dictionary.get('recoverSfdcObjectParams') else None
        recover_to = dictionary.get('recoverTo')
        recovery_action = dictionary.get('recoveryAction')

        return cls(
            continue_on_error,
            objects,
            recover_sfdc_object_params,
            recover_to,
            recovery_action
        )
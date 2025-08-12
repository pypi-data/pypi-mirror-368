# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_of_day
import cohesity_management_sdk.models_v2.sla_rule

class CommonBackupParams(object):

    """Implementation of the 'CommonBackupParams' model.

    Specifies the common parameters for backup. These parameters are common
    across protection group and object protection.

    Attributes:
        policy_id (string): Specifies the unique id of the Protection Policy.
            The Policy settings will be attached with every object and will be
            used in backup.
        storage_domain_id (long|int): Specifies the Storage Domain (View Box)
            ID where the object backup will be taken. This is not required if
            Cloud archive direct is benig used.
        start_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.
        priority (PriorityEnum): Specifies the priority for the objects
            backup.
        sla (list of SlaRule): Specifies the SLA parameters for list of
            objects.
        qos_policy (QosPolicyEnum): Specifies whether object backup will be
            written to HDD or SSD.
        abort_in_blackouts (bool): Specifies whether currently executing
            object backup should abort if a blackout period specified by a
            policy starts. Available only if the selected policy has at least
            one blackout period. Default value is false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "policy_id":'policyId',
        "storage_domain_id":'storageDomainId',
        "start_time":'startTime',
        "priority":'priority',
        "sla":'sla',
        "qos_policy":'qosPolicy',
        "abort_in_blackouts":'abortInBlackouts'
    }

    def __init__(self,
                 policy_id=None,
                 storage_domain_id=None,
                 start_time=None,
                 priority=None,
                 sla=None,
                 qos_policy=None,
                 abort_in_blackouts=None):
        """Constructor for the CommonBackupParams class"""

        # Initialize members of the class
        self.policy_id = policy_id
        self.storage_domain_id = storage_domain_id
        self.start_time = start_time
        self.priority = priority
        self.sla = sla
        self.qos_policy = qos_policy
        self.abort_in_blackouts = abort_in_blackouts


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
        policy_id = dictionary.get('policyId')
        storage_domain_id = dictionary.get('storageDomainId')
        start_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None
        priority = dictionary.get('priority')
        sla = None
        if dictionary.get("sla") is not None:
            sla = list()
            for structure in dictionary.get('sla'):
                sla.append(cohesity_management_sdk.models_v2.sla_rule.SlaRule.from_dictionary(structure))
        qos_policy = dictionary.get('qosPolicy')
        abort_in_blackouts = dictionary.get('abortInBlackouts')

        # Return an object of this model
        return cls(policy_id,
                   storage_domain_id,
                   start_time,
                   priority,
                   sla,
                   qos_policy,
                   abort_in_blackouts)



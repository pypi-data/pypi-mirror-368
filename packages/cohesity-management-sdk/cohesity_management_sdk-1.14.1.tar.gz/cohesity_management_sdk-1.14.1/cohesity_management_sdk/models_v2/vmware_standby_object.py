# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.m_o_ref


class VmwareStandbyObject(object):

    """Implementation of the 'VmwareStandbyObject' model.

   Specifies the VMware specific standby object details.

    Attributes:
        entity_id (long|int): Specifies the entity id of the corresponding backup object for
          which this standby is configured.
        protection_group_id (string): Specifies the protection group id to which this standby object
          belongs.
        cdp_standby_status (CdpStandbyStatusEnum): Specifies the current status of the standby object protected
            using continuous data protection policy.
        guest_id (string): Specifies the guest ID(OS) of the standby VM for the corresponding
            backup object.
        standby_m_o_ref (MOref): Specifies the MORef of the standby VM created on VMware environments.
        standby_time (long|int): Specifies the time till which the standby object has been hydrated
            for the corresponding backup object.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "entity_id":'entityId',
        "protection_group_id":'protectionGroupId',
        "cdp_standby_status":'CdpStandbyStatus',
        "guest_id":'guestId',
        "standby_m_o_ref":'standbyMOref',
        "standby_time":'standbyTime'
    }

    def __init__(self,
                 entity_id=None,
                 protection_group_id=None,
                 cdp_standby_status=None,
                 guest_id=None,
                 standby_m_o_ref=None,
                 standby_time=None):
        """Constructor for the VmwareStandbyObject class"""

        # Initialize members of the class
        self.entity_id = entity_id
        self.protection_group_id = protection_group_id
        self.cdp_standby_status = cdp_standby_status
        self.guest_id = guest_id
        self.standby_m_o_ref = standby_m_o_ref
        self.standby_time = standby_time



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
        entity_id = dictionary.get('entityId')
        protection_group_id = dictionary.get('protectionGroupId')
        cdp_standby_status = dictionary.get('CdpStandbyStatus')
        guest_id = dictionary.get('guestId')
        standby_m_o_ref = cohesity_management_sdk.models_v2.m_o_ref.MORef.from_dictionary(dictionary.get('standbyMOref')) if dictionary.get('standbyMOref') else None
        standby_time = dictionary.get('standbyTime')


        # Return an object of this model
        return cls(entity_id,
                   protection_group_id,
                   cdp_standby_status,
                   guest_id,
                   standby_m_o_ref,
                   standby_time)
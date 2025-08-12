# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.vmware_cdp_object
import cohesity_management_sdk.models_v2.m_o_ref


class VmwareObjectEntityParams(object):

    """Implementation of the 'VmwareObjectEntityParams' model.

    Object details for Vmware.

    Attributes:
        cdp_info (VmwareCdpObject): Specifies the Continuous Data Protection (CDP) details about
          this object. This is only available if this object if protected by a CDP
          enabled policy.
        is_template (bool): Specifies if the object is a VM template.
        mo_ref (MOREf): Specifies the managed object reference to the object (w.r.t vCenter).
        mtype (Type27Enum): VMware Object type.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cdp_info":'cdpInfo',
        "is_template":'isTemplate',
        "mo_ref":'moRef',
        "mtype":'type'
    }

    def __init__(self,
                 cdp_info=None,
                 is_template=None,
                 mo_ref=None,
                 mtype=None):
        """Constructor for the VmwareObjectEntityParams class"""

        # Initialize members of the class
        self.cdp_info = cdp_info
        self.is_template = is_template
        self.mo_ref = mo_ref
        self.mtype = mtype


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
        cdp_info = cohesity_management_sdk.models_v2.vmware_cdp_object.VmwareCdpObject.from_dictionary(dictionary.get('cdpInfo')) if dictionary.get('cdpInfo') else None
        is_template = dictionary.get('isTemplate')
        mo_ref = cohesity_management_sdk.models_v2.m_o_ref.MORef.from_dictionary(dictionary.get('moRef')) if dictionary.get('moRef') else None
        mtype = dictionary.get('type')

        # Return an object of this model
        return cls(
                   cdp_info,
                   is_template,
                   mo_ref,
                   mtype)
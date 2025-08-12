# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_site_param
import cohesity_management_sdk.models_v2.recovery_object_identifier
import cohesity_management_sdk.models_v2.target_site_param

class RecoverSiteParams(object):

    """Implementation of the 'Recover Site params.' model.

    Specifies the parameters to recover Microsoft Office 365 Sharepoint
      site.

    Attributes:
        continue_on_error (bool): Specifies whether to continue recovering the doc libs of a site,
          if one or more of doc libs failed to recover. Default value is false.
        objects (list of ObjectSiteParam): Specifies a list of site params associated with the objects to
          recover.
        recover_preservation_hold_library (bool): Specifies whether to recover Preservation Hold Library associated
          with the Sites selected for restore. Default value is false.
        target_domain_object_id (RecoveryObjectIdentifier): Specifies the object id of the target domain in case of full
          recovery of a site to a target domain.
        target_site (TargetSiteParam): Specifies the target Site to recover to. If not specified, the
          objects will be recovered to original location.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "continue_on_error":'continueOnError',
        "objects":'objects',
        "recover_preservation_hold_library":'recoverPreservationHoldLibrary',
        "target_domain_object_id":'targetDomainObjectId',
        "target_site":'targetSite'
    }

    def __init__(self,
                 continue_on_error=None,
                 objects=None,
                 recover_preservation_hold_library=None,
                 target_domain_object_id=None,
                 target_site=None):
        """Constructor for the RecoverSiteParams class"""

        # Initialize members of the class
        self.continue_on_error = continue_on_error
        self.objects = objects
        self.recover_preservation_hold_library = recover_preservation_hold_library
        self.target_domain_object_id = target_domain_object_id
        self.target_site = target_site


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
        continue_on_error = dictionary.get('continueOnError')
        objects =None
        if dictionary.get('objects') is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.object_site_param.ObjectSiteParam.from_dictionary(structure))
        recover_preservation_hold_library = dictionary.get('recoverPreservationHoldLibrary')
        target_domain_object_id = cohesity_management_sdk.models_v2.recovery_object_identifier.RecoveryObjectIdentifier.from_dictionary(dictionary.get('targetDomainObjectId')) if dictionary.get('targetDomainObjectId') else None
        target_site = cohesity_management_sdk.models_v2.target_site_param.TargetSiteParam.from_dictionary(dictionary.get('targetSite')) if dictionary.get('targetSite') else None

        # Return an object of this model
        return cls(continue_on_error,
                   objects,
                   recover_preservation_hold_library,
                   target_domain_object_id,
                   target_site)
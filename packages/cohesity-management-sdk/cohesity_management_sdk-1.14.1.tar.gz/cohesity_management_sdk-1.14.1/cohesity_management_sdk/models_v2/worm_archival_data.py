# -*- coding: utf-8 -*-


class WormArchivalData(object):

    """Implementation of the 'WormProperties' model.

    Specifies the WORM related properties for this archive.

    Attributes:
        is_archive_worm_compliant (bool): Specifies whether this archive run is WORM compliant
        worm_expiry_time_usecs (long|int): Specifies the time at which the WORM protection expires.
        worm_non_compliance_reason (string): Specifies reason of archive not being worm compliant.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "is_archive_worm_compliant":'isArchiveWormCompliant',
        "worm_expiry_time_usecs":'wormExpiryTimeUsecs',
        "worm_non_compliance_reason":'wormNonComplianceReason'
    }

    def __init__(self,
                 is_archive_worm_compliant=None,
                 worm_expiry_time_usecs=None,
                 worm_non_compliance_reason=None):
        """Constructor for the WormArchivalData class"""

        # Initialize members of the class
        self.is_archive_worm_compliant = is_archive_worm_compliant
        self.worm_expiry_time_usecs = worm_expiry_time_usecs
        self.worm_non_compliance_reason = worm_non_compliance_reason


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
        is_archive_worm_compliant = dictionary.get('isArchiveWormCompliant')
        worm_expiry_time_usecs = dictionary.get('wormExpiryTimeUsecs')
        worm_non_compliance_reason = dictionary.get('wormNonComplianceReason')

        # Return an object of this model
        return cls(is_archive_worm_compliant,
                   worm_expiry_time_usecs,
                   worm_non_compliance_reason)
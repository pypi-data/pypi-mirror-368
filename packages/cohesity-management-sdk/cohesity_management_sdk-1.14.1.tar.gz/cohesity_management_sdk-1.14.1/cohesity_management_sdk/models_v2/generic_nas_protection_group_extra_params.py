# -*- coding: utf-8 -*-


class GenericNasProtectionGroupExtraParams(object):

    """Implementation of the 'GenericNasProtectionGroupExtraParams' model.

    Specifies the extra parameters which are specific to NAS related
    Protection Groups.

    Attributes:
        direct_cloud_archive (bool): Specifies whether or not to store the
            snapshots in this run directly in an Archive Target instead of on
            the Cluster. If this is set to true, the associated policy must
            have exactly one Archive Target associated with it and the policy
            must be set up to archive after every run. Also, a Storage Domain
            cannot be specified. Default behavior is 'false'.
        native_format (bool): Specifies whether or not to enable native format
            for direct archive job. This field is set to true if native format
            should be used for archiving.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "direct_cloud_archive":'directCloudArchive',
        "native_format":'nativeFormat'
    }

    def __init__(self,
                 direct_cloud_archive=None,
                 native_format=None):
        """Constructor for the GenericNasProtectionGroupExtraParams class"""

        # Initialize members of the class
        self.direct_cloud_archive = direct_cloud_archive
        self.native_format = native_format


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
        direct_cloud_archive = dictionary.get('directCloudArchive')
        native_format = dictionary.get('nativeFormat')

        # Return an object of this model
        return cls(direct_cloud_archive,
                   native_format)



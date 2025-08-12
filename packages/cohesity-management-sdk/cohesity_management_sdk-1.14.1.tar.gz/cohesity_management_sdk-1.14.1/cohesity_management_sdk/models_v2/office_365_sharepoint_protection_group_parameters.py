# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.office_365_preservation_hold_library_params

class Office365SharepointProtectionGroupParameters(object):

    """Implementation of the 'OOffice365SharepointProtectionGroupParameters' model.

    Specifies the parameters which are specific to Office 365 SharePoint
      related Protection Groups.

    Attributes:
        exclude_paths (list of string): Array of paths to be excluded from backup. Specifies list of
          doclib/directory paths which should be excluded when backing up Office 365
          source. supported exclusion: - doclib exclusion: whole doclib is excluded
          from backup. sample: /Doclib1 - directory exclusion: specified path in doclib
          will be excluded from backup. sample: /Doclib1/folderA/forderB Doclibs can
          be specified by either a) Doclib name - eg, Documents. b) Drive id of doclib
          - b!ZMSl2JRm0UeXLHfHR1m-iuD10p0CIV9qSa6TtgM Regular expressions are not
          supported. If not specified, all the doclibs within sharepoint site will
          be protected.
        preservation_hold_library_params (Office365PreservationHoldLibraryParams):
          Specifies the parameters specific to the protection of the Preservation
          Hold library.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "exclude_paths":'excludePaths',
        "preservation_hold_library_params":'preservationHoldLibraryParams'
    }

    def __init__(self,
                 exclude_paths=None,
                 preservation_hold_library_params=None):
        """Constructor for the Office365O365OutlookProtectionGroupParameters class"""

        # Initialize members of the class
        self.exclude_paths = exclude_paths
        self.preservation_hold_library_params = preservation_hold_library_params


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
        exclude_paths = dictionary.get('excludePaths')
        preservation_hold_library_params = cohesity_management_sdk.models_v2.office_365_preservation_hold_library_params.Office365PreservationLibraryHoldParams.from_dictionary(dictionary.get('preservationHoldLibraryParams')) if dictionary.get('preservationHoldLibraryParams') else None

        # Return an object of this model
        return cls(exclude_paths,
                   preservation_hold_library_params)
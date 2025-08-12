# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.specifies_the_tag_information_of_type_and_array_of_label_value
import cohesity_management_sdk.models_v2.progress_summary

class DataTieringAnalysisInfo(object):

    """Implementation of the 'DataTieringAnalysisInfo' model.

    Specifies the data tiering analysis details.

    Attributes:
        tags_info (list of
            SpecifiesTheTagInformationOfTypeAndArrayOfLabelValue): Array of
            Tag objects.
        progress (ProgressSummary): Specifies the progress summary.
        status (Status9Enum): Status of the analysis run. 'Running' indicates
            that the run is still running. 'Canceled' indicates that the run
            has been canceled. 'Canceling' indicates that the run is in the
            process of being  canceled. 'Failed' indicates that the run has
            failed. 'Missed' indicates that the run was unable to take place
            at the  scheduled time because the previous run was still
            happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run
            finished  successfully, but there were some warning messages.
            'OnHold' indicates that the run has On hold.
        message (string): message from the last analysis run stating the error
            message in case of error in analysis run or warning message if the
            run finished successfully, but there were some warning messages.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "tags_info":'tagsInfo',
        "progress":'progress',
        "status":'status',
        "message":'message'
    }

    def __init__(self,
                 tags_info=None,
                 progress=None,
                 status=None,
                 message=None):
        """Constructor for the DataTieringAnalysisInfo class"""

        # Initialize members of the class
        self.tags_info = tags_info
        self.progress = progress
        self.status = status
        self.message = message


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
        tags_info = None
        if dictionary.get("tagsInfo") is not None:
            tags_info = list()
            for structure in dictionary.get('tagsInfo'):
                tags_info.append(cohesity_management_sdk.models_v2.specifies_the_tag_information_of_type_and_array_of_label_value.SpecifiesTheTagInformationOfTypeAndArrayOfLabelValue.from_dictionary(structure))
        progress = cohesity_management_sdk.models_v2.progress_summary.ProgressSummary.from_dictionary(dictionary.get('progress')) if dictionary.get('progress') else None
        status = dictionary.get('status')
        message = dictionary.get('message')

        # Return an object of this model
        return cls(tags_info,
                   progress,
                   status,
                   message)



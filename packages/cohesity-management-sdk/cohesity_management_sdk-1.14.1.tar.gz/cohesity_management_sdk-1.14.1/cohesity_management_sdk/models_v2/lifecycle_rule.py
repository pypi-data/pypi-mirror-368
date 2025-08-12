# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.abort_incomplete_multipart_upload_action
import cohesity_management_sdk.models_v2.expiration_action
import cohesity_management_sdk.models_v2.lifecycle_rule_filter
from cohesity_management_sdk.models_v2.non_current_version_expiration_action import NonCurrentVersionExpirationAction

class LifecycleRule(object):

    """Implementation of the 'LifecycleRule' model.

    Specifies the Lifecycle configuration rule.

    Attributes:
        abort_incomplete_multipart_upload_action (AbortIncompleteMultipartUploadAction): Specifies the days since the initiation of an incomplete multipart
          upload before permanently removing all parts of the upload.
        expiration (ExpirationAction): Specifies the expiration for the lifecycle of the object in the
          form of date, days and whether the object has a delete marker.
        filter (LifecycleRuleFilter): Specifies the filter used to identify objects that a Lifecycle
          Rule applies to.
        id (string): Specifies the Unique identifier for the rule. The value cannot
          be longer than 255 characters.
        non_current_version_expiration_action (NonCurrentVersionExpirationAction): Specifies when non-current object versions expire. Upon expiration,
          non-current object versions are permanently deleted. The action can be specified
          only in versioning enabled or suspended buckets.
        prefix (string): Specifies the prefix used to identify objects that a lifecycle
          rule applies to.
        status (bool): Specifies if the rule is currently being applied.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "abort_incomplete_multipart_upload_action":'abortIncompleteMultipartUploadAction',
        "expiration":'expiration',
        "filter":'filter',
        "id":'id',
        "non_current_version_expiration_action":'nonCurrentVersionExpirationAction',
        "prefix":'prefix',
        "status":'status'
    }

    def __init__(self,
                 abort_incomplete_multipart_upload_action=None,
                 expiration=None,
                 filter=None,
                 id=None,
                 non_current_version_expiration_action=None,
                 prefix=None,
                 status=None):
        """Constructor for the LifecycleRule class"""

        # Initialize members of the class
        self.abort_incomplete_multipart_upload_action = abort_incomplete_multipart_upload_action
        self.expiration = expiration
        self.filter = filter
        self.id = id
        self.non_current_version_expiration_action = non_current_version_expiration_action
        self.prefix = prefix
        self.status = status

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
        abort_incomplete_multipart_upload_action = cohesity_management_sdk.models_v2.abort_incomplete_multipart_upload_action.AbortIncompleteMultipartUploadAction.from_dictionary(dictionary.get('abortIncompleteMultipartUploadAction')) if dictionary.get('abortIncompleteMultipartUploadAction') else None
        expiration = cohesity_management_sdk.models_v2.expiration_action.ExpirationAction.from_dictionary(dictionary.get('expiration')) if dictionary.get('expiration') else None
        filter = cohesity_management_sdk.models_v2.lifecycle_rule_filter.LifecycleRuleFilter.from_dictionary(dictionary.get('filter')) if dictionary.get('filter') else None
        id = dictionary.get('id')
        non_current_version_expiration_action = NonCurrentVersionExpirationAction.from_dictionary(dictionary.get('nonCurrentVersionExpirationAction')) if dictionary.get('nonCurrentVersionExpirationAction') else None
        prefix = dictionary.get('prefix')
        status = dictionary.get('status')


        # Return an object of this model
        return cls(abort_incomplete_multipart_upload_action,
                   expiration,
                   filter,
                   id,
                   non_current_version_expiration_action,
                   prefix,
                   status
                   )
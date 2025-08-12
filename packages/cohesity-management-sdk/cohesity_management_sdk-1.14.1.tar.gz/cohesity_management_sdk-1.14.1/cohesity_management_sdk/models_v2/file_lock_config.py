# -*- coding: utf-8 -*-


class FileLockConfig(object):

    """Implementation of the 'FileLockConfig' model.


    Specifies a config to lock files in a view - to protect from malicious or
    an accidental attempt to delete or modify the files in this view.

    Attributes:
        auto_lock_after_duration_idle_msecs (int): Specifies the duration to
            lock a file that has not been accessed or modified (ie. has been
            idle) for a certain duration of time in milliseconds. Do not set
            if it is required to disable auto lock.
        coexisting_lock_mode (bool): Specified if files in the View can be
            locked in different modes. This property is immutable and can only
            be set when enabling File level datalock. If this property is set
            for an S3 View, S3 bucket Versioning should also be enabled.
        default_retention_duration_msecs (long|int): Specifies a global
            default retention duration for files in this view, if file lock is
            enabled for this view. Also, it is a required field if file lock
            is enabled. Set to -1 if the required default retention period is
            forever.
        default_retention_duration_years (long|int): Specifies a global default
            retention duration in years for files in this view, if file/object
            lock is enabled for this view.
        expiry_timestamp_msecs (int): Specifies a definite timestamp in
            milliseconds for retaining the file.
        ignore_existing_files (bool): If set, implicit locking will be applied
            only to the newly created or updated inodes.
        locking_protocol (LockingProtocolEnum): Specifies the supported
            mechanisms to explicity lock a file from NFS/SMB interface.
            Supported locking protocols: SetReadOnly, SetAtime. 'SetReadOnly'
            is compatible with Isilon/Netapp behaviour. This locks the file
            and the retention duration is determined in this order: 1) atime,
            if set by user/application and within min and max retention
            duration. 2) Min retention duration, if set. 3) Otherwise, file is
            switched to expired data automatically. 'SetAtime' is compatible
            with Data Domain behaviour.
        max_retention_duration_msecs (long|int): Specifies a maximum duration
            in milliseconds for which any file in this view can be retained
            for. Set to -1 if the required retention duration is forever. If
            set, it should be greater than or equal to the default retention
            period as well as the min retention period.
        min_retention_duration_msecs (long|int): Specifies a minimum retention
            duration in milliseconds after a file gets locked. The file cannot
            be modified or deleted during this timeframe. Set to -1 if the
            required retention duration is forever. This should be set less
            than or equal to the default retention duration.
        mode (Mode2Enum): Specifies the mode of file level datalock.
            Enterprise mode can be upgraded to Compliance mode, but Compliance
            mode cannot be downgraded to Enterprise mode. Compliance: This
            mode would disallow all user to delete/modify file or view under
            any condition when it 's in locked status except for deleting view
            when the view is empty. Enterprise: This mode would follow the
            rules as compliance mode for normal users. But it would allow the
            storage admin (1) to delete view or file anytime no matter it is
            in locked status or expired. (2) to rename the view (3) to bring
            back the retention period when it's in locked mode A lock mode of
            a file in a view can be in one of the following: 'Compliance':
            Default mode of datalock, in this mode, Data Security Admin cannot
            modify/delete this view when datalock is in effect. Data Security
            Admin can delete this view when datalock is expired. 'kEnterprise'
            : In this mode, Data Security Admin can change view name or delete
            view when datalock is in effect. Datalock in this mode can be
            upgraded to 'Compliance' mode.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "auto_lock_after_duration_idle_msecs":'autoLockAfterDurationIdleMsecs',
        "coexisting_lock_mode":'coexistingLockMode',
        "default_retention_duration_msecs":'defaultRetentionDurationMsecs',
        "default_retention_duration_years":'defaultRetentionDurationYears',
        "expiry_timestamp_msecs":'expiryTimestampMsecs',
        "ignore_existing_files":'ignoreExistingFiles',
        "locking_protocol":'lockingProtocol',
        "max_retention_duration_msecs":'maxRetentionDurationMsecs',
        "min_retention_duration_msecs":'minRetentionDurationMsecs',
        "mode":'mode'
    }

    def __init__(self,
                 auto_lock_after_duration_idle_msecs=None,
                 coexisting_lock_mode=None,
                 default_retention_duration_msecs=None,
                 default_retention_duration_years=None,
                 expiry_timestamp_msecs=None,
                 ignore_existing_files=None,
                 locking_protocol=None,
                 max_retention_duration_msecs=None,
                 min_retention_duration_msecs=None,
                 mode=None):
        """Constructor for the FileLockConfig class"""

        # Initialize members of the class
        self.auto_lock_after_duration_idle_msecs = auto_lock_after_duration_idle_msecs
        self.coexisting_lock_mode = coexisting_lock_mode
        self.default_retention_duration_msecs = default_retention_duration_msecs
        self.default_retention_duration_years = default_retention_duration_years
        self.expiry_timestamp_msecs = expiry_timestamp_msecs
        self.ignore_existing_files = ignore_existing_files
        self.locking_protocol = locking_protocol
        self.max_retention_duration_msecs = max_retention_duration_msecs
        self.min_retention_duration_msecs = min_retention_duration_msecs
        self.mode = mode


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
        auto_lock_after_duration_idle_msecs = dictionary.get('autoLockAfterDurationIdleMsecs')
        coexisting_lock_mode = dictionary.get('coexistingLockMode')
        default_retention_duration_msecs = dictionary.get('defaultRetentionDurationMsecs')
        default_retention_duration_years = dictionary.get('defaultRetentionDurationYears')
        expiry_timestamp_msecs = dictionary.get('expiryTimestampMsecs')
        ignore_existing_files = dictionary.get('ignoreExistingFiles')
        locking_protocol = dictionary.get('lockingProtocol')
        max_retention_duration_msecs = dictionary.get('maxRetentionDurationMsecs')
        min_retention_duration_msecs = dictionary.get('minRetentionDurationMsecs')
        mode = dictionary.get('mode')

        # Return an object of this model
        return cls(auto_lock_after_duration_idle_msecs,
                   coexisting_lock_mode,
                   default_retention_duration_msecs,
                   default_retention_duration_years,
                   expiry_timestamp_msecs,
                   ignore_existing_files,
                   locking_protocol,
                   max_retention_duration_msecs,
                   min_retention_duration_msecs,
                   mode)



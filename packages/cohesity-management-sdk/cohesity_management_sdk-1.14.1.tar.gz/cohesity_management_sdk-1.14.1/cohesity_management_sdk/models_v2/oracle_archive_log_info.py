# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models_v2.oracle_range_meta_info

class OracleArchiveLogInfo(object):
    """Implementation of the 'OracleArchiveLogInfo' model.

    Specifies information related to archive log restore.

    Attributes:
        archive_log_restore_dest (string): Specifies destination where archive logs are to be restored.
        range_info_vec (OracleRangeMetaInfo): Specifies an array of oracle restore ranges.
        range_type (RangeTypeEnum): Specifies the type of range.
    """

    _names = {
        "archive_log_restore_dest":"archiveLogRestoreDest",
        "range_info_vec":"rangeInfoVec",
        "range_type":"rangeType",
    }

    def __init__(self,
                 archive_log_restore_dest=None,
                 range_info_vec=None,
                 range_type=None):
        """Constructor for the OracleArchiveLogInfo class"""

        self.archive_log_restore_dest = archive_log_restore_dest
        self.range_info_vec = range_info_vec
        self.range_type = range_type


    @classmethod
    def from_dictionary(cls, dictionary):
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

        archive_log_restore_dest = dictionary.get('archiveLogRestoreDest')
        range_info_vec = None
        if dictionary.get('rangeInfoVec') is not None:
            range_info_vec = list()
            for structure in dictionary.get('rangeInfoVec'):
                range_info_vec.append(cohesity_management_sdk.models_v2.oracle_range_meta_info.OracleRangeMetaInfo.from_dictionary(structure))
        range_type = dictionary.get('rangeType')

        return cls(
            archive_log_restore_dest,
            range_info_vec,
            range_type
        )
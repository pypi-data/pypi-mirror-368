# -*- coding: utf-8 -*-
import cohesity_management_sdk.models_v2.compression_params
import cohesity_management_sdk.models_v2.deduplication_parameters
import cohesity_management_sdk.models_v2.erasure_coding_parameters


class StoragePolicy(object):

    """Implementation of the 'Storage Policy' model.

    Specifies the storage policy of a Storage Domain.

    Attributes:
        aes_encryption_mode (aesEncryptionModeEnum): Specifies the encryption mode for a Storage Domain.
        app_marker_detection_enabled (bool): Specifies whether app marker detection is enabled. When enabled,
          app markers will be removed from data and put in separate chunks.
        cloud_spill_vault_id (long|int): Specifies the vault id assigned for cloud spill for a Storage
          Domain.
        compression_params (CompressionParams): Specifies compression settings for a Storage Domain.
        deduplication_compression_Delay_secs (long|int): Specifies the time in seconds when deduplication and compression
          of the Storage Domain starts.
        deduplication_params (DeduplicationParams): Specifies deduplication settings for a Storage Domain.
        encryption_type (EncryptionTypeEnum): Specifies the encryption type for a Storage Domain.
        erasure_coding_params (ErasureCodingParams): Specifies the erasure coding parameters for a Storage Domain.
        num_disk_failures_tolerated (long|int): Specifies the number of disk failures to tolerate for a Storage
          Domain. By default, this field is 1 for cluster with three or more nodes.
          If erasure coding is enabled, this field will be the same as numCodedStripes.
        num_node_failures_tolerated (long|int): Specifies the number of node failures to tolerate for a Storage
          Domain. By default this field is replication factor minus 1 for replication
          chunk files and is the same as numCodedStripes for erasure coding chunk
          files.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aes_encryption_mode":'aesEncryptionMode',
        "app_marker_detection_enabled":'appMarkerDetectionEnabled',
        "cloud_spill_vault_id":'cloudSpillVaultId',
        "compression_params":'compressionParams',
        "deduplication_compression_Delay_secs":'deduplicationCompressionDelaySecs',
        "deduplication_params":'deduplicationParams',
        "encryption_type":'encryptionType',
        "erasure_coding_params":'erasureCodingParams',
        "num_disk_failures_tolerated":'numDiskFailuresTolerated',
        "num_node_failures_tolerated":'numNodeFailuresTolerated'
    }

    def __init__(self,
                 aes_encryption_mode=None,
                 app_marker_detection_enabled=None,
                 cloud_spill_vault_id=None,
                 compression_params=None,
                 deduplication_compression_Delay_secs=None,
                 deduplication_params=None,
                 encryption_type=None,
                 erasure_coding_params=None,
                 num_disk_failures_tolerated=None,
                 num_node_failures_tolerated=None
                 ):
        """Constructor for the StoragePolicy class"""

        # Initialize members of the class
        self.aes_encryption_mode = aes_encryption_mode
        self.app_marker_detection_enabled = app_marker_detection_enabled
        self.cloud_spill_vault_id = cloud_spill_vault_id
        self.compression_params = compression_params
        self.deduplication_compression_Delay_secs = deduplication_compression_Delay_secs
        self.deduplication_params = deduplication_params
        self.encryption_type = encryption_type
        self.erasure_coding_params = erasure_coding_params
        self.num_disk_failures_tolerated = num_disk_failures_tolerated
        self.num_node_failures_tolerated = num_node_failures_tolerated

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
        aes_encryption_mode = dictionary.get('aesEncryptionMode')
        app_marker_detection_enabled = dictionary.get('appMarkerDetectionEnabled')
        cloud_spill_vault_id = dictionary.get('cloudSpillVaultId')
        compression_params = cohesity_management_sdk.models_v2.compression_params.CompressionParams.from_dictionary(dictionary.get('compressionParams')) if dictionary.get('compressionParams') else None
        deduplication_compression_Delay_secs = dictionary.get('deduplicationCompressionDelaySecs')
        deduplication_params = cohesity_management_sdk.models_v2.deduplication_parameters.DeduplicationParameters.from_dictionary(dictionary.get('deduplicationParams')) if dictionary.get('deduplicationParams') else None
        encryption_type = dictionary.get('encryptionType')
        erasure_coding_params = cohesity_management_sdk.models_v2.erasure_coding_parameters.ErasureCodingParameters.from_dictionary(dictionary.get('erasureCodingParams')) if dictionary.get('erasureCodingParams') else None
        num_disk_failures_tolerated = dictionary.get('numDiskFailuresTolerated')
        num_node_failures_tolerated = dictionary.get('numNodeFailuresTolerated')

        # Return an object of this model
        return cls(aes_encryption_mode,
                   app_marker_detection_enabled,
                   cloud_spill_vault_id,
                   compression_params,
                   deduplication_compression_Delay_secs,
                   deduplication_params,
                   encryption_type,
                   erasure_coding_params,
                   num_disk_failures_tolerated,
                   num_node_failures_tolerated)
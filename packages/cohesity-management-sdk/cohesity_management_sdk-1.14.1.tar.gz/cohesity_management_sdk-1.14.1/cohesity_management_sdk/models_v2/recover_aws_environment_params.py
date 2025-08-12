# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_aws_aurora_params_1
import cohesity_management_sdk.models_v2.download_file_and_folder_params
import cohesity_management_sdk.models_v2.recover_aws_s_3_params
import cohesity_management_sdk.models_v2.recover_awsvm_params
import cohesity_management_sdk.models_v2.recover_aws_file_and_folder_params
import cohesity_management_sdk.models_v2.recover_rds_params
import cohesity_management_sdk.models_v2.recover_rds_postgres_params

class RecoverAWSEnvironmentParams(object):

    """Implementation of the 'Recover AWS environment params.' model.

    Specifies the recovery options specific to AWS environment.

    Attributes:
        download_file_and_folder_params (DownloadFileAndFolderParams): Specifies the parameters to download files and folders.
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters. This property is mandatory for
            all recovery action types except recover vms. While recovering
            VMs, a user can specify snapshots of VM's or a Protection Group
            Run details to recover all the VM's that are backed up by that
            Run. For recovering files, specifies the object contains the file
            to recover.
        recovery_action (RecoveryAction2Enum): Specifies the type of recover
            action to be performed.
        recover_vm_params (RecoverAWSVMParams): Specifies the parameters to
            recover AWS VM.
        recover_aurora_params (RecoverAWSAuroraParams1): Specifies the parameters to recover AWS Aurora.
        recover_file_and_folder_params (RecoverAWSFileAndFolderParams):
            Specifies the parameters to recover files and folders.
        recover_rds_params (RecoverRdsParams): Specifies the parameters to AWS
            RDS.
        recover_rds_ingest_params (RecoverRdsPostgresParams): Specifies the parameters to recover AWS RDS Ingest.
        recover_s_3_bucket_params (RecoverAWSS3Params): Specifies the parameters to recover AWS S3 Buckets.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "download_file_and_folder_params":'downloadFileAndFolderParams',
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_vm_params":'recoverVmParams',
        "recover_aurora_params":'recoverAuroraParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "recover_rds_params":'recoverRdsParams',
        "recover_rds_ingest_params":'recoverRdsIngestParams',
        "recover_s_3_bucket_params":'recoverS3BucketParams'
    }

    def __init__(self,
                 download_file_and_folder_params=None,
                 recovery_action=None,
                 objects=None,
                 recover_vm_params=None,
                 recover_aurora_params=None,
                 recover_file_and_folder_params=None,
                 recover_rds_params=None,
                 recover_rds_ingest_params=None,
                 recover_s_3_bucket_params=None):

        """Constructor for the RecoverAWSEnvironmentParams class"""

        # Initialize members of the class
        self.download_file_and_folder_params = download_file_and_folder_params
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_vm_params = recover_vm_params
        self.recover_aurora_params = recover_aurora_params
        self.recover_file_and_folder_params = recover_file_and_folder_params
        self.recover_rds_params = recover_rds_params
        self.recover_rds_ingest_params = recover_rds_ingest_params
        self.recover_s_3_bucket_params = recover_s_3_bucket_params


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
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(
            dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None
        recovery_action = dictionary.get('recoveryAction')
        objects = None
        if dictionary.get("objects") is not None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_vm_params = cohesity_management_sdk.models_v2.recover_awsvm_params.RecoverAWSVMParams.from_dictionary(dictionary.get('recoverVmParams')) if dictionary.get('recoverVmParams') else None
        recover_aurora_params = cohesity_management_sdk.models_v2.recover_aws_aurora_params_1.RecoverAWSAuroraParams1.from_dictionary(dictionary.get('recoverAuroraParams')) if dictionary.get('recoverAuroraParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_aws_file_and_folder_params.RecoverAWSFileAndFolderParams.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        recover_rds_params = cohesity_management_sdk.models_v2.recover_rds_params.RecoverRdsParams.from_dictionary(dictionary.get('recoverRdsParams')) if dictionary.get('recoverRdsParams') else None
        recover_rds_ingest_params = cohesity_management_sdk.models_v2.recover_rds_postgres_params.RecoverRdsPostgresParams.from_dictionary(dictionary.get('recoverRdsIngestParams')) if dictionary.get('recoverRdsIngestParams') else None
        recover_s_3_bucket_params = cohesity_management_sdk.models_v2.recover_aws_s_3_params.RecoverAWSS3Params.from_dictionary(
            dictionary.get('recoverS3BucketParams')) if dictionary.get('recoverS3BucketParams') else None

        # Return an object of this model
        return cls(download_file_and_folder_params,
                   recovery_action,
                   objects,
                   recover_vm_params,
                   recover_aurora_params,
                   recover_file_and_folder_params,
                   recover_rds_params,
                   recover_rds_ingest_params,
                   recover_s_3_bucket_params)
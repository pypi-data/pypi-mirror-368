# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_parameters
import cohesity_management_sdk.models_v2.azure_parameters
import cohesity_management_sdk.models_v2.cloud_spin_data_statistics
import cohesity_management_sdk.models_v2.data_lock_constraints

class CloudSpinResultForATarget(object):

    """Implementation of the 'Cloud Spin result for a target.' model.

    Cloud Spin result for a target.

    Attributes:
        aws_params (AwsParameters): Specifies various resources when
            converting and deploying a VM to AWS.
        azure_params (AzureCloudSpinParams): Specifies various resources when
            converting and deploying a VM to Azure.
        cloudspin_task_id (string): Task ID for a CloudSpin protection run.
        data_lock_constraints (DataLockConstraints): Specifies the dataLock
            constraints for local or target snapshot.
        end_time_usecs (long|int): Specifies the end time of Cloud Spin in Unix epoch Timestamp(in
            microseconds) for a target.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in Unix epoch Timestamp
            (in microseconds) for an object.
        id (long|int): Specifies the unique id of the cloud spin entity.
        is_manually_deleted (bool): Specifies whether the snapshot is deleted manually.
        message (string): Message about the Cloud Spin run.
        name (string): Specifies the name of the already added cloud spin target.
        on_legal_hand (bool): Specifies the legal hold status for a cloud spin target.
        progress_task_id (string): Progress monitor task id for Cloud Spin
            run.
        start_time_usecs (long|int): Specifies the start time of Cloud Spin in
            Unix epoch Timestamp(in microseconds) for a target.
        stats (CloudSpinDataStatistics): Specifies statistics about Cloud Spin
            data.
        status (Status7Enum): Status of the Cloud Spin for a target. 'Running'
            indicates that the run is still running. 'Canceled' indicates that
            the run has been canceled. 'Canceling' indicates that the run is
            in the process of being canceled. 'Failed' indicates that the run
            has failed. 'Missed' indicates that the run was unable to take
            place at the scheduled time because the previous run was still
            happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run
            finished successfully, but there were some warning messages.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aws_params":'awsParams',
        "azure_params":'azureParams',
        "cloudspin_task_id":'cloudspinTaskId',
        "data_lock_constraints":'dataLockConstraints',
        "end_time_usecs":'endTimeUsecs',
        "expiry_time_usecs":'expiryTimeUsecs',
        "id":'id',
        "is_manually_deleted":'isManuallyDeleted',
        "message":'message',
        "name":'name',
        "on_legal_hold":'onLegalHold',
        "progress_task_id":'progressTaskId',
        "start_time_usecs":'startTimeUsecs',
        "stats":'stats',
        "status":'status'
    }

    def __init__(self,
                 aws_params=None,
                 azure_params=None,
                 cloudspin_task_id=None,
                 data_lock_constraints=None,
                 end_time_usecs=None,
                 expiry_time_usecs=None,
                 id=None,
                 is_manually_deleted=None,
                 message=None,
                 name=None,
                 on_legal_hold=None,
                 progress_task_id=None,
                 start_time_usecs=None,
                 stats=None,
                 status=None
                 ):
        """Constructor for the CloudSpinResultForATarget class"""

        # Initialize members of the class
        self.aws_params = aws_params
        self.azure_params = azure_params
        self.cloudspin_task_id = cloudspin_task_id
        self.data_lock_constraints = data_lock_constraints
        self.end_time_usecs = end_time_usecs
        self.expiry_time_usecs = expiry_time_usecs
        self.id = id
        self.is_manually_deleted = is_manually_deleted
        self.message = message
        self.name = name
        self.on_legal_hold = on_legal_hold
        self.progress_task_id = progress_task_id
        self.start_time_usecs = start_time_usecs
        self.stats = stats
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
        aws_params = cohesity_management_sdk.models_v2.aws_parameters.AWSParameters.from_dictionary(dictionary.get('awsParams')) if dictionary.get('awsParams') else None
        azure_params = cohesity_management_sdk.models_v2.azure_parameters.AzureParameters.from_dictionary(dictionary.get('azureParams')) if dictionary.get('azureParams') else None
        cloudspin_task_id = dictionary.get('cloudspinTaskId')
        data_lock_constraints = cohesity_management_sdk.models_v2.data_lock_constraints.DataLockConstraints.from_dictionary(dictionary.get('dataLockConstraints')) if dictionary.get('dataLockConstraints') else None
        end_time_usecs = dictionary.get('endTimeUsecs')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        id = dictionary.get('id')
        is_manually_deleted = dictionary.get('isManuallyDeleted')
        message = dictionary.get('message')
        name = dictionary.get('name')
        on_legal_hold = dictionary.get('onLegalHold')
        progress_task_id = dictionary.get('progressTaskId')
        start_time_usecs = dictionary.get('startTimeUsecs')
        stats = cohesity_management_sdk.models_v2.cloud_spin_data_statistics.CloudSpinDataStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        status = dictionary.get('status')


        # Return an object of this model
        return cls(aws_params,
                   azure_params,
                   cloudspin_task_id,
                   data_lock_constraints,
                   end_time_usecs,
                   expiry_time_usecs,
                   id,
                   is_manually_deleted,
                   message,
                   name,
                   on_legal_hold,
                   progress_task_id,
                   start_time_usecs,
                   stats,
                   status)
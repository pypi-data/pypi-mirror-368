# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_env_job_params
import cohesity_management_sdk.models_v2.common_mssql_protection_group_request_params
import cohesity_management_sdk.models_v2.san_env_job_params
import cohesity_management_sdk.models_v2.physical_env_job_params
import cohesity_management_sdk.models_v2.oracle_env_job_params
import cohesity_management_sdk.models_v2.o_365_env_job_params
import cohesity_management_sdk.models_v2.nas_env_job_params
import cohesity_management_sdk.models_v2.hyperv_env_job_params
import cohesity_management_sdk.models_v2.externally_triggered_job_params
import cohesity_management_sdk.models_v2.exchange_env_job_params
import cohesity_management_sdk.models_v2.aws_snapshot_manager_params

class EnvironmentTypeJobParams(object):

    """Implementation of the 'EnvironmentTypeJobParams' model.

    Specifies the policy level additional environment specific backup
      params. If this is not specified, default actions will be taken, for example
      for NAS environments, all objects within the source will be backed up.

    Attributes:
        aws_snapshot_params (AwsSnapshotManagerParams): Specifies additional special
           parameters that are applicable only to snaphot manger jobs.
        exchange_params (ExchangeEnvJobParams): Specifies additional special parameters that are applicable only
          to Types of 'kExchange' type.
        externally_triggered_job_params (ExternallyTriggeredJobParams): Specifies additional special parameters that are applicable only
          to externally triggered backup jobs of 'kView' type.
        hyperv_params (HypervEnvJobParams): Specifies additional special parameters that are applicable only
          to Types of 'kHyperV' type.
        nas_params (NasEnvJobParams): Specifies additional special parameters that are applicable only
          to Types of 'kGenericNas' type.
        office_365_params (O365EnvJobParams): Specifies additional special parameters that are applicable only
          to types of 'kO365Outlook' type which incorporates both Mailbox & OneDrive
          backup parameters.
        oracle_params (OracleEnvJobParams): Specifies additional special parameters that are applicable only
          to Types of 'kOracle' type.
        physical_params (PhysicalEnvJobParams): Specifies additional special parameters that are applicable only
          to Sources of 'kPhysical' type in a kPhysical environment.
        pure_params (): Specifies additional special parameters that are applicable only
          to SAN Types.
        sql_params (CommonMSSQLProtectionGroupRequestParams): Specifies additional special parameters that are applicable only
          to Types of 'kSQL' type.
        vmware_params (VmwareEnvJobParams): Specifies additional special parameters that are applicable only
          to Types of 'kVMware' type.
    """

    # Create a mapping from Model property names to API property names
    _names = {
        "aws_snapshot_params":"awsSnapshotParams" ,
        "exchange_params":"exchangeParams",
        "externally_triggered_job_params":"externallyTriggeredJobParams",
        "hyperv_params":"hypervParams",
        "nas_params":"nasParams",
        "office_365_params":"office365Params",
        "oracle_params":"oracleParams",
        "physical_params":'physicalParams',
        "pure_params":'pureParams',
        "sql_params":'sqlParams',
        "vmware_params":'vmwareParams'
    }

    def __init__(self,
                 aws_snapshot_params=None,
                 exchange_params=None,
                 externally_triggered_job_params=None,
                 hyperv_params=None,
                 nas_params=None,
                 office_365_params=None,
                 oracle_params=None,
                 physical_params=None,
                 pure_params=None,
                 sql_params=None,
                 vmware_params=None):
        """Constructor for the EnvironmentTypeJobParams class"""

        # Initialize members of the class
        self.aws_snapshot_params = aws_snapshot_params
        self.exchange_params = exchange_params
        self.externally_triggered_job_params = externally_triggered_job_params
        self.hyperv_params = hyperv_params
        self.nas_params = nas_params
        self.office_365_params = office_365_params
        self.oracle_params = oracle_params
        self.physical_params  = physical_params
        self.pure_params = pure_params
        self.sql_params = sql_params
        self.vmware_params = vmware_params


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
        aws_snapshot_params = cohesity_management_sdk.models_v2.aws_snapshot_manager_params.AwsSnapshotManagerParams.from_dictionary(
            dictionary.get('awsSnapshotParams')) if dictionary.get('awsSnapshotParams') else None
        exchange_params = cohesity_management_sdk.models_v2.exchange_env_job_params.ExchangeEnvJobParams.from_dictionary(
            dictionary.get('exchangeParams')) if dictionary.get('exchangeParams') else None
        externally_triggered_job_params = cohesity_management_sdk.models_v2.externally_triggered_job_params.ExternallyTriggeredJobParams.from_dictionary(
            dictionary.get('externallyTriggeredJobParams')) if dictionary.get('externallyTriggeredJobParams') else None
        hyperv_params = cohesity_management_sdk.models_v2.hyperv_env_job_params.HypervEnvJobParams.from_dictionary(
            dictionary.get('hypervParams')) if dictionary.get('hypervParams') else None
        nas_params = cohesity_management_sdk.models_v2.nas_env_job_params.NasEnvJobParams.from_dictionary(
            dictionary.get('nasParams')) if dictionary.get('nasParams') else None
        office_365_params = cohesity_management_sdk.models_v2.o_365_env_job_params.O365EnvJobParams.from_dictionary(
            dictionary.get('office365Params')) if dictionary.get('office365Params') else None
        oracle_params = cohesity_management_sdk.models_v2.oracle_env_job_params.OracleEnvJobParams.from_dictionary(
            dictionary.get('oracleParams')) if dictionary.get('oracleParams') else None
        physical_params = cohesity_management_sdk.models_v2.physical_env_job_params.PhysicalEnvJobParams.from_dictionary(dictionary.get('physicalParams')) if dictionary.get('physicalParams') else None
        pure_params = cohesity_management_sdk.models_v2.san_env_job_params.SanEnvJobParams.from_dictionary(dictionary.get('pureParams')) if dictionary.get('pureParams') else None
        sql_params = cohesity_management_sdk.models_v2.common_mssql_protection_group_request_params.CommonMSSQLProtectionGroupRequestParams.from_dictionary(dictionary.get('sqlParams')) if dictionary.get('sqlParams') else None
        vmware_params = cohesity_management_sdk.models_v2.vmware_env_job_params.VmwareEnvJobParams.from_dictionary(dictionary.get('vmwareParams')) if dictionary.get('vmwareParams') else None

        # Return an object of this model
        return cls(
              aws_snapshot_params,
              exchange_params,
              externally_triggered_job_params,
              hyperv_params,
              nas_params,
              office_365_params,
              oracle_params,
              physical_params,
              pure_params,
              sql_params,
              vmware_params)
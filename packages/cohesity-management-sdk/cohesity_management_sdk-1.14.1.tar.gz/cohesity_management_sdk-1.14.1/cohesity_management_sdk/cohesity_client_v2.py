# -*- coding: utf-8 -*-

from cohesity_management_sdk.decorators import lazy_property
from cohesity_management_sdk.configuration_v2 import ConfigurationV2
from cohesity_management_sdk.controllers_v2.active_directory_controller import ActiveDirectoryController
from cohesity_management_sdk.controllers_v2.platform_controller import PlatformController
from cohesity_management_sdk.controllers_v2.audit_log_controller import AuditLogController
from cohesity_management_sdk.controllers_v2.security_controller import SecurityController
from cohesity_management_sdk.controllers_v2.data_migration_controller import DataMigrationController
from cohesity_management_sdk.controllers_v2.miscellaneous_controller import MiscellaneousController
from cohesity_management_sdk.controllers_v2.objects_controller import ObjectsController
from cohesity_management_sdk.controllers_v2.protection_policies_controller import ProtectionPoliciesController
from cohesity_management_sdk.controllers_v2.protection_groups_controller import ProtectionGroupsController
from cohesity_management_sdk.controllers_v2.recoveries_controller import RecoveriesController
from cohesity_management_sdk.controllers_v2.search_controller import SearchController
from cohesity_management_sdk.controllers_v2.protection_sources_controller import ProtectionSourcesController
from cohesity_management_sdk.controllers_v2.views_controller import ViewsController
from cohesity_management_sdk.controllers_v2.keystone_controller import KeystoneController
from cohesity_management_sdk.controllers_v2.network_information_service_nis_controller import NetworkInformationServiceNISController
from cohesity_management_sdk.controllers_v2.patches_controller import PatchesController
from cohesity_management_sdk.controllers_v2.users_controller import UsersController
from cohesity_management_sdk.controllers_v2.stats_controller import StatsController
from cohesity_management_sdk.controllers_v2.tasks_controller import TasksController
from cohesity_management_sdk.controllers_v2.test_data_management_controller import TestDataManagementController
from cohesity_management_sdk.controllers_v2.tenants_controller import TenantsController


class CohesityClientV2(object):


    @lazy_property
    def active_directory(self):
        return ActiveDirectoryController(self.config)

    @lazy_property
    def platform(self):
        return PlatformController(self.config)

    @lazy_property
    def audit_log(self):
        return AuditLogController(self.config)

    @lazy_property
    def security(self):
        return SecurityController(self.config)

    @lazy_property
    def data_migration(self):
        return DataMigrationController(self.config)

    @lazy_property
    def miscellaneous(self):
        return MiscellaneousController(self.config)

    @lazy_property
    def objects(self):
        return ObjectsController(self.config)

    @lazy_property
    def protection_policies(self):
        return ProtectionPoliciesController(self.config)

    @lazy_property
    def protection_groups(self):
        return ProtectionGroupsController(self.config)

    @lazy_property
    def recoveries(self):
        return RecoveriesController(self.config)

    @lazy_property
    def search(self):
        return SearchController(self.config)

    @lazy_property
    def protection_sources(self):
        return ProtectionSourcesController(self.config)

    @lazy_property
    def views(self):
        return ViewsController(self.config)

    @lazy_property
    def keystone(self):
        return KeystoneController(self.config)

    @lazy_property
    def network_information_service_nis(self):
        return NetworkInformationServiceNISController(self.config)

    @lazy_property
    def patches(self):
        return PatchesController(self.config)

    @lazy_property
    def users(self):
        return UsersController(self.config)

    @lazy_property
    def stats(self):
        return StatsController(self.config)

    @lazy_property
    def tasks(self):
        return TasksController(self.config)

    @lazy_property
    def test_data_management(self):
        return TestDataManagementController(self.config)

    @lazy_property
    def tenants(self):
        return TenantsController(self.config)


    def __init__(self,
                 cluster_vip=None,
                 username=None,
                 password=None,
                 domain=None,
                 auth_token=None,
                 api_key=None,
                 session_id=None,
                 use_session=None):

        self.config = ConfigurationV2()

        if cluster_vip is None:
            raise Exception("Specify cluster VIP")
        if auth_token is not None:
            self.config.auth_token = auth_token
        if username is not None:
            self.config.username = username
        if password is not None:
            self.config.password = password
            self.config.auth_token = None  # Flushing existing token.
        if domain is not None:
            self.config.domain = domain
        self.config.cluster_vip = cluster_vip
        if api_key is not None:
            self.config.api_key = api_key
        if session_id is not None:
            self.config.session_id = session_id
        if use_session is not None:
            self.config.use_session = use_session
# -*- coding: utf-8 -*-
# Copyright 2024 Cohesity Inc.

import cohesity_management_sdk.models.entity_proto
import cohesity_management_sdk.models.restore_site_params_site_owner
import cohesity_management_sdk.models.site_backup_status


class RestoreSiteParams(object):

    """Implementation of the 'RestoreSiteParams' model.

    TODO: type description here.


    Attributes:

        dst_site_name (string): Entity name of target site in case of
            sharepoint restore.
        dst_site_uuid (string): Entity uuid of target site in case of
            sharepoint restore.
        dst_site_web_url (string): Entity web url of target site in case of
            sharepoint restore.
        parent_source_sharepoint_domain_name (string): The sharepoint domain
            name of the registered parent source from which the site is backed
            up.
        phl_restore_prefix (string): This prefix is pre-pended to the doc lib
            which is created for recovering PHL.
            This must be set if restore_phl_drive is set to true.
        restore_phl_drive (bool): When set to true, the preservation hold
            library (PHL) drive for the site should be restored.
        restore_template (bool): Indicates that we have to restore the
            Sharepoint site template also. This includes: 1) Create site if it
            does not exist. 2) Provision template.
        restore_to_original (bool): Whether or not all sites are restored to
            original location.
        restore_user_doclibs_before_provisioning_template (bool): Whether user doclibs should be restored before provisioning site
          template.
        should_restore_lists (bool):  Whether lists should be restore for this
            site restore.
        site_owner_vec (list of RestoreSiteParams_SiteOwner): The list of sites
            whose drives are being restored.
        site_result (SiteBackupStatus): Site template backup status returned by
            the agent on successful site backup.
        site_version (int): Versions for site restores. There can be
            incompatible changes across process restarts or across restores. To
            avoid issues, maintain a version for restore.
        skip_client_side_page_files_upload (bool): Whether pnp library should upload files linked to client side pages while
          provisioning template. This should be set if and only if files download
          was skipped during backup with the flag
          magneto_o365spo_pnp_pwsh_skip_site_page_files_for_domains. In this case,
          magneto_sharepoint_restore_user_doclibs_before_template_for_domains must
          also be set to restore site page references correctly.
        snap_fs_relative_site_backup_result_path (string): SnapFS relative path
            where the site template backup result proto is stored.
        snap_fs_relative_template_path (string): SnapFS relative path where the
            template data is stored.
        source_site_name (string): Entity name of source site in case of
            sharepoint restore.
        source_site_uuid (string): Entity uuid of source site in case of
            sharepoint restore.
        source_web_url (string): Entity web url of source site in case of
            sharepoint restore.
        target_doc_lib_name (string): Incase of alternate restore of granular
            items within document repositiories of sites to another site, a doc
            lib name has to be specified by the caller. NOTE: It can be safely
            assumed that this field will only be present in case of granular
            items restore only.
        target_doc_lib_prefix (string): If alternate site is provided, customer
            may want to provide a custom prefix to document libraries that we
            create. In any case we would also have to distinguish the newly
            created document library as the alternate site provided by the
            customer may as well turn out to be the original backup site.
        target_folder_path_prefix (string): Target folder path prefix for
            granular restore. This is set in case of teams or groups restore.
        target_site (EntityProto): This is the site in whose drive the items
            will be restored.
    """


    # Create a mapping from Model property names to API property names
    _names = {
        "dst_site_name":'dstSiteName',
        "dst_site_uuid":'dstSiteUuid',
        "dst_site_web_url":'dstSiteWebUrl',
        "parent_source_sharepoint_domain_name":'parentSourceSharepointDomainName',
        "phl_restore_prefix": 'phlRestorePrefix',
        "restore_phl_drive": 'restorePhlDrive',
        "restore_template":'restoreTemplate',
        "restore_to_original":'restoreToOriginal',
        "restore_user_doclibs_before_provisioning_template":'restoreUserDoclibsBeforeProvisioningTemplate',
        "should_restore_lists": 'shouldRestoreLists',
        "site_owner_vec":'siteOwnerVec',
        "site_result":'siteResult',
        "site_version":'siteVersion',
        "skip_client_side_page_files_upload":'skipClientSidePageFilesUpload',
        "snap_fs_relative_site_backup_result_path":'snapFsRelativeSiteBackupResultPath',
        "snap_fs_relative_template_path":'snapFsRelativeTemplatePath',
        "source_site_name":'sourceSiteName',
        "source_site_uuid":'sourceSiteUuid',
        "source_web_url":'sourceWebUrl',
        "target_doc_lib_name":'targetDocLibName',
        "target_doc_lib_prefix":'targetDocLibPrefix',
        "target_folder_path_prefix":'targetFolderPathPrefix',
        "target_site":'targetSite',
    }
    def __init__(self,
                 dst_site_name=None,
                 dst_site_uuid=None,
                 dst_site_web_url=None,
                 parent_source_sharepoint_domain_name=None,
                 phl_restore_prefix=None,
                 restore_phl_drive=None,
                 restore_template=None,
                 restore_to_original=None,
                 restore_user_doclibs_before_provisioning_template=None,
                 should_restore_lists=None,
                 site_owner_vec=None,
                 site_result=None,
                 site_version=None,
                 skip_client_side_page_files_upload=None,
                 snap_fs_relative_site_backup_result_path=None,
                 snap_fs_relative_template_path=None,
                 source_site_name=None,
                 source_site_uuid=None,
                 source_web_url=None,
                 target_doc_lib_name=None,
                 target_doc_lib_prefix=None,
                 target_folder_path_prefix=None,
                 target_site=None,
            ):

        """Constructor for the RestoreSiteParams class"""

        # Initialize members of the class
        self.dst_site_name = dst_site_name
        self.dst_site_uuid = dst_site_uuid
        self.dst_site_web_url = dst_site_web_url
        self.parent_source_sharepoint_domain_name = parent_source_sharepoint_domain_name
        self.phl_restore_prefix = phl_restore_prefix
        self.restore_phl_drive = restore_phl_drive
        self.restore_template = restore_template
        self.restore_to_original = restore_to_original
        self.restore_user_doclibs_before_provisioning_template = restore_user_doclibs_before_provisioning_template
        self.should_restore_lists = should_restore_lists
        self.site_owner_vec = site_owner_vec
        self.site_result = site_result
        self.site_version = site_version
        self.skip_client_side_page_files_upload = skip_client_side_page_files_upload
        self.snap_fs_relative_site_backup_result_path = snap_fs_relative_site_backup_result_path
        self.snap_fs_relative_template_path = snap_fs_relative_template_path
        self.source_site_name = source_site_name
        self.source_site_uuid = source_site_uuid
        self.source_web_url = source_web_url
        self.target_doc_lib_name = target_doc_lib_name
        self.target_doc_lib_prefix = target_doc_lib_prefix
        self.target_folder_path_prefix = target_folder_path_prefix
        self.target_site = target_site

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
        dst_site_name = dictionary.get('dstSiteName')
        dst_site_uuid = dictionary.get('dstSiteUuid')
        dst_site_web_url = dictionary.get('dstSiteWebUrl')
        parent_source_sharepoint_domain_name = dictionary.get('parentSourceSharepointDomainName')
        phl_restore_prefix = dictionary.get('phlRestorePrefix')
        restore_phl_drive = dictionary.get('restorePhlDrive')
        restore_template = dictionary.get('restoreTemplate')
        restore_to_original = dictionary.get('restoreToOriginal')
        restore_user_doclibs_before_provisioning_template = dictionary.get('restoreUserDoclibsBeforeProvisioningTemplate')
        should_restore_lists = dictionary.get('shouldRestoreLists')
        site_owner_vec = None
        if dictionary.get("siteOwnerVec") is not None:
            site_owner_vec = list()
            for structure in dictionary.get('siteOwnerVec'):
                site_owner_vec.append(cohesity_management_sdk.models.restore_site_params_site_owner.RestoreSiteParams_SiteOwner.from_dictionary(structure))
        site_result = cohesity_management_sdk.models.site_backup_status.SiteBackupStatus.from_dictionary(dictionary.get('siteResult')) if dictionary.get('siteResult') else None
        site_version = dictionary.get('siteVersion')
        skip_client_side_page_files_upload = dictionary.get('skipClientSidePageFilesUpload')
        snap_fs_relative_site_backup_result_path = dictionary.get('snapFsRelativeSiteBackupResultPath')
        snap_fs_relative_template_path = dictionary.get('snapFsRelativeTemplatePath')
        source_site_name = dictionary.get('sourceSiteName')
        source_site_uuid = dictionary.get('sourceSiteUuid')
        source_web_url = dictionary.get('sourceWebUrl')
        target_doc_lib_name = dictionary.get('targetDocLibName')
        target_doc_lib_prefix = dictionary.get('targetDocLibPrefix')
        target_folder_path_prefix = dictionary.get('targetFolderPathPrefix')
        target_site = cohesity_management_sdk.models.entity_proto.EntityProto.from_dictionary(dictionary.get('targetSite')) if dictionary.get('targetSite') else None

        # Return an object of this model
        return cls(
            dst_site_name,
            dst_site_uuid,
            dst_site_web_url,
            parent_source_sharepoint_domain_name,
            phl_restore_prefix,
            restore_phl_drive,
            restore_template,
            restore_to_original,
            restore_user_doclibs_before_provisioning_template,
            should_restore_lists,
            site_owner_vec,
            site_result,
            site_version,
            skip_client_side_page_files_upload,
            snap_fs_relative_site_backup_result_path,
            snap_fs_relative_template_path,
            source_site_name,
            source_site_uuid,
            source_web_url,
            target_doc_lib_name,
            target_doc_lib_prefix,
            target_folder_path_prefix,
            target_site
)
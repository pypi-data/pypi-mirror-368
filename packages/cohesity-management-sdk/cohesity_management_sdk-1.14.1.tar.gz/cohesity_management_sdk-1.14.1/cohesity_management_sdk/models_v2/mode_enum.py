# -*- coding: utf-8 -*-

class ModeEnum(object):

    """Implementation of the 'Mode' enum.

    Specifies how the permission should be applied to folders and/or files.
    'FolderSubFoldersAndFiles' indicates that permissions are applied to a
    Folder
    and it's sub folders and files.
    'FolderAndSubFolders' indicates that permissions are applied to a Folder
    and it's sub folders.
    'FolderAndSubFiles' indicates that permissions are applied to a Folder and
    it's sub files.
    'FolderOnly' indicates that permsission are applied to folder only.
    'SubFoldersAndFilesOnly' indicates that permissions are applied to sub
    folders and files only.
    'SubFoldersOnly' indicates that permissiona are applied to sub folders
    only.
    'FilesOnly' indicates that permissions are applied to files only.

    Attributes:
        FOLDERSUBFOLDERSANDFILES: TODO: type description here.
        FOLDERANDSUBFOLDERS: TODO: type description here.
        FOLDERANDFILES: TODO: type description here.
        FOLDERONLY: TODO: type description here.
        SUBFOLDERSANDFILESONLY: TODO: type description here.
        SUBFOLDERSONLY: TODO: type description here.
        FILESONLY: TODO: type description here.

    """

    FOLDERSUBFOLDERSANDFILES = 'FolderSubFoldersAndFiles'

    FOLDERANDSUBFOLDERS = 'FolderAndSubFolders'

    FOLDERANDFILES = 'FolderAndFiles'

    FOLDERONLY = 'FolderOnly'

    SUBFOLDERSANDFILESONLY = 'SubFoldersAndFilesOnly'

    SUBFOLDERSONLY = 'SubFoldersOnly'

    FILESONLY = 'FilesOnly'


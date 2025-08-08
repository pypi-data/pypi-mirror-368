from file_golem import AbstractDatatype, FileDatatypes, FilePathEntries
import os



class PathSeperatorDatatype(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.EMPTY
    SYSTEM_CONFIG_SPECIFIED_PATH = 'system_config_specified_path'

    @staticmethod
    def _split_path(data_args):
        base_path = data_args[PathSeperatorDatatype.SYSTEM_CONFIG_SPECIFIED_PATH]
        return base_path.split(os.sep)

class ProjectDatatype(PathSeperatorDatatype):
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        {FilePathEntries.CUSTOM_LOGIC: '_split_path'},
    )


class OverleafDirectory(PathSeperatorDatatype):
    OVERLEAF_SUBDIR = 'overleaf_subdir'

    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        {FilePathEntries.CUSTOM_LOGIC: '_split_overleaf_path'},
    )

    @staticmethod
    def _split_overleaf_path(data_args):
        overleaf_subdir = data_args[OverleafDirectory.OVERLEAF_SUBDIR]
        return overleaf_subdir.split(os.sep)


class OverleafDatatype(OverleafDirectory):
    OVERLEAF_SUBDIR = 'overleaf_subdir'

    RELATIVE_PATH_TUPLE = OverleafDirectory.RELATIVE_PATH_TUPLE + (
        {FilePathEntries.CUSTOM_LOGIC: '_split_path'},
    )

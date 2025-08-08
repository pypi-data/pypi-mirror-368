from enum import Enum

class FileDatatypes(Enum):
    MATPLOTLIB = 'matplotlib'
    PANDAS = 'pandas'
    JSON = 'json'
    TEXT = 'text'
    TORCH = 'torch'
    TORCH_CHECKPOINT = 'torch_checkpoint'
    PICKLE = 'pickle'
    PNG = 'png'
    PDF = 'pdf'
    NUMPY = 'numpy'
    OMEGA_CONF = 'omega_conf'
    EMPTY = 'empty'
    SHELL = 'shell'
    SLURM_SCRIPT = 'slurm_script'
    SLURM_OUTPUT_STD = 'slurm_output_std'
    SLURM_OUTPUT_ERR = 'slurm_output_err'
    JPEG = 'jpeg'
    JPEG_BOLD = 'jpeg_bold'
    
class SpecialDataArgs(Enum):
    DATA_IO = 'data_io'
    DATA_TYPE = 'data_type'
    SUPPORTED_FILETYPES = 'supported_filetypes'
    DEFAULTS = 'defaults'
    SYSTEM_PATHS = 'system_paths'
    IGNORE_PRIMARY_DATA_PREFIX_LIST = 'ignore_primary_data_prefix'
    EXTERNAL_CALLS = 'external_calls'
    ENTRY_POINT = 'entry_point'
    CONDA_PATH = 'conda_path'
    PYTHON_ENTRY_POINT = 'python_entry_point'
    OVERLEAF_SUBDIR = 'overleaf_subdir'
    OVERLEAF_MAPPINGS = 'overleaf_mappings'

    ORIGIN_CONFIG = 'origin_config'
    ORIGIN_MODULE = 'origin_module'

class FilePathEntries(Enum):
    BASE_DATA_DIRECTORY = 'base_data_directory'
    IDX_ENTRY = 'idx_entry'
    MODULATED_IDX_ENTRY = 'modulated_idx_entry'
    ZERO_PADDED_IDX_ENTRY = 'zero_padded_idx_entry' #Use for zero padded idx entries
    ATTRIBUTE_ENTRY = 'attribute_entry'
    DATA_TYPE_ENTRY = 'data_type_entry'
    OPEN_ENTRY = 'open_entry' #Use as a place holder when iterating over files
    CONFIG_ENTRY = 'config_entry' #Use for parsing config title. This ensures that the seperators are handled correctly
    TIMESTAMP_CONFIG_ENTRY = 'timestamp_config_entry' #Use primarily for slurm outputs
    DATA_ARG_ENTRY = 'data_arg_entry' #Use as a dict key for processing the tuple
    CUSTOM_LOGIC = 'custom_logic' #call into a function to get the entry value

class AbstractDatatype:
    DATA = 'data'
    IDX = 'idx'
    FILE_DATATYPE = None #Assign a value from the FileDatatypes enum here
    CONFIG_NAME = 'config_name'
    TIMESTAMP = 'timestamp_config_entry_timestamp'
    USE_ONLY_RELATIVE_PATH = False  # If True, the relative path will be used instead of the absolute path. Strongly discouraged for most datatypes.
    IS_EXECUTABLE = False  # If True, the datatype is executable (e.g., shell scripts, slurm scripts). If set to True, file_golem will automatically add the executable permission to the file.
    CAN_PRINT_ON_DEBUG = True  # If True, the datatype can be printed on debug. If set to False, the datatype will not be printed on debug.
    RELATIVE_PATH_TUPLE = (
        FilePathEntries.BASE_DATA_DIRECTORY,
    )

    @staticmethod
    def _custom_length_logic(data_args):
        datatype = data_args[SpecialDataArgs.DATA_TYPE]
        raise Exception(f'Custom length logic (the static method _custom_length_logic(data_args)) not implemented for datatype {datatype.__name__}.')
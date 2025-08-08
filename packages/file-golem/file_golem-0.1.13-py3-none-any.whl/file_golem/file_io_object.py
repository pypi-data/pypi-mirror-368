import os
import glob
import subprocess
from filelock import FileLock
from omegaconf import OmegaConf
from omegaconf.listconfig import ListConfig
import shutil
import inspect
import stat
from datetime import datetime

from file_golem._file_io_helper import _initialize_load_save_extension_dicts, get_file_size, _calculate_timestamp_length
from file_golem.file_datatypes import FileDatatypes, FilePathEntries, AbstractDatatype,SpecialDataArgs
from file_golem.config_datatype import Config
from file_golem.class_handler import ClassHandler



_sentinel = object()

class FileGolem:
    DATA_DIRECTORY_NAME = 'data_directory_name'
    PROJECT_BASE_DIRECTORY = 'base_data_directory'
    FILELOCK_TIMEOUT_KEY = 'filelock_timeout'
    MAX_INDEXED_DIRECTORY_SIZE = 'max_indexed_directory_size'
    SYSTEM_TRANSFERS = 'system_transfers'
    PROJECT_SRC_ROOT = 'project_src_root'
    HAS_DUPLICATE_MODULE_NAMES = 'has_duplicate_module_names'
    SYSTEM_IDENTITY_FILE = 'system_identity_file'
    AUX_FILETYPES_FN  = 'aux_filetypes_fn'
    BASE_CONDA_NAME = 'base_conda_name'
    CAN_ADD_GROUP_PERMISSIONS_ON_SAVE = 'can_add_group_permissions_on_save'
    SLURM_SERVER_CREDENTIALS = 'slurm_server_credentials'
    SLURM_PROJECT_DIRECTORY = 'slurm_project_directory'



    def __init__(self, system_config = None, system_config_path = None,is_debug=False, system_transfer=None):
        self.timestamp_format = '%m-%d_%H:%M:%S'
        self.system_config = system_config
        self.system_config_path = system_config_path
        self.system_transfer = system_transfer

        self.is_debug = is_debug
        self.lengths_cache = {}
        self.config_cache = {}
        self.no_print_on_debug_set = set()
        self.load_system_config()
        self.load_system_identity()
        self.load_absolute_path_prefix()
        self.load_can_add_group_permissions_on_save()

        self.base_data_directory_name = self.system_config.get(self.DATA_DIRECTORY_NAME, 'data')

        self.class_handler = ClassHandler(
            project_src_root=self.system_config.get(self.PROJECT_SRC_ROOT, 'src'),
            has_duplicate_module_names=self.system_config.get(self.HAS_DUPLICATE_MODULE_NAMES, False),
        )

        self.load_file_extension_dicts()





    def load_system_config(self):
        if self.system_config is not None:
            return

        if self.system_config_path is None:
            raise Exception('You must pass either a system_config or system_config_path to the FileGolem constructor')
        
        self.load_function_dict, \
        self.save_function_dict, \
        self.file_extension_dict = _initialize_load_save_extension_dicts([FileDatatypes.OMEGA_CONF.value], None)

        self.system_config = self.load_config(self.system_config_path)
            
    #TODO: We should rework configs- they ought to be their own objects, as the functionality is quite complex.
    def load_config(self,config_path,ancestry=[]):
        if config_path in self.config_cache:
            return self.config_cache[config_path]
        if config_path in ancestry:
            raise Exception(f'Cycle detected in config inheritance: {ancestry}')
        
        config =self.load_data(Config, data_args = {
            Config.CONFIG_NAME: config_path
        })

        ancestry = ancestry + [config_path]
        config = self._handle_defaults(config, ancestry)        
        self.config_cache[config_path] = config
        return config

    def fetch_subconfig(self, config_or_config_name, subconfig_keys):

        if isinstance(config_or_config_name, str):
            subconfig  = self.load_config(config_or_config_name)
        else:
            subconfig = self._handle_defaults(config_or_config_name) # Always handle defaults for subconfig if passed directly
        
        if len(subconfig_keys) == 0:
            return subconfig
        
        key = subconfig_keys[0]

        assert isinstance(key, str), 'subconfig_keys must be a list of strings'

        if OmegaConf.is_list(subconfig):
            for item in subconfig:
                if OmegaConf.is_dict(item) and (key in item) and len(item) == 1:
                    subconfig = item[key]
                    return self.fetch_subconfig(subconfig, subconfig_keys[1:])
            return {}
        else:
            if key in subconfig:
                subconfig = subconfig[key]
                return self.fetch_subconfig(subconfig, subconfig_keys[1:])
            else:
                return {}
            

    def extract_architecture_information(self,global_config_name):
        module_list_subconfig_keys = self._create_origin_subconfig_keys()
        module_list = self.fetch_config_field(
            global_config_name,
            subconfig_keys =module_list_subconfig_keys)
        
        if isinstance(module_list, str):
            print(f'warning: architecture: {module_list} is a deprecated format. Please change to: ')
            print(f'architecture:\n    origin_config: {module_list}')
            print(f'architecture:\n    origin_module: <module_1, or module_2, ...>')
            raise Exception('Please change the architecture format to the new format. See the documentation for more details.')
        
        if isinstance(module_list, ListConfig):
            model_module_names = [list(module.keys())[0] for module in module_list]
        else:
            model_module_names = [None]


        origin_configs = []
        instantiate_module_names = []
        is_external_configs = []
        instantiate_configs = []

        for module_name in model_module_names:

            origin_config, origin_module_name, is_external_config,instantiate_config = self.handle_recursive_module_references(
                global_config_name,
                module_name
            )


            origin_configs.append(origin_config)
            instantiate_module_names.append(origin_module_name)
            is_external_configs.append(is_external_config)
            instantiate_configs.append(instantiate_config)

        return origin_configs, instantiate_module_names, is_external_configs,instantiate_configs, model_module_names

    def _create_origin_subconfig_keys(self,module_name=None):
        """
        Creates the subconfig keys for the origin config based on the module name.
        This is used to fetch the origin config from the system config.
        """
        subconfig_keys = ['architecture', 'module_list']
        if module_name is not None:
            subconfig_keys.append(module_name)
        return subconfig_keys
    
    def _handle_defaults(self,config, ancestry=[]):
        if OmegaConf.is_list(config): #list types cannot call the .get function
            return config
        
        if SpecialDataArgs.ORIGIN_CONFIG.value in config:
            origin_config_full = self.load_config(config[SpecialDataArgs.ORIGIN_CONFIG.value], ancestry)
            module_name = config.get(SpecialDataArgs.ORIGIN_MODULE.value, None)
            
            subconfig_keys = self._create_origin_subconfig_keys(module_name)
            origin_config_default = self.fetch_subconfig(
                origin_config_full,
                subconfig_keys=subconfig_keys,)
            
            # if config[SpecialDataArgs.ORIGIN_CONFIG.value] == 'conf/ctrl_exps/ctrl_infinity_base.yaml':
            #     print('loading here')
            #     print(subconfig_keys)
            #     print(origin_config_default)
            #     print(config)
            #     print(OmegaConf.merge(origin_config_default, config))
            #     raise Exception('stack trace')
            
            config = OmegaConf.merge(origin_config_default, config)


        ### Handle Standard Defaults
        defaults_list = config.get(SpecialDataArgs.DEFAULTS.value,[])
        for default_config_path in defaults_list:
            default_config = self.load_config(default_config_path,ancestry)
            config = OmegaConf.merge(default_config,config)
        return config

    def handle_recursive_module_references(self, module_config,module_name,is_external_config=False,architecture=OmegaConf.create({})):
        subconfig_keys = self._create_origin_subconfig_keys(module_name)
        origin_config = self.fetch_subconfig(module_config, subconfig_keys= subconfig_keys)
        origin_config = OmegaConf.merge(origin_config, architecture)

        origin_config_name = self.fetch_config_field(
            module_config,
            subconfig_keys=subconfig_keys+[SpecialDataArgs.ORIGIN_CONFIG.value],
            default=None)
        
        if origin_config_name is None:
            return module_config, module_name, is_external_config,origin_config
        
        origin_module_name = self.fetch_config_field(
            module_config,
            subconfig_keys=subconfig_keys+[SpecialDataArgs.ORIGIN_MODULE.value],
            default=None)

        return self.handle_recursive_module_references(origin_config_name, origin_module_name, True,origin_config)


    

    def fetch_config_field(self,config_or_config_name, subconfig_keys = [],default=_sentinel):
        assert isinstance(subconfig_keys, list), 'subconfig_keys must be a list' 
        subconfig = self.fetch_subconfig(config_or_config_name,subconfig_keys[:-1])
        if not subconfig:
            if default is _sentinel:
                raise Exception(f'No subconfig found for keys {subconfig_keys} in config {config_or_config_name}, and no default value provided')
            else:
                return default
            
        if OmegaConf.is_list(subconfig):
            raise Exception(f'Subconfig {subconfig} is a list, but expected a dictionary. Please check the config structure. TODO: include support for lists as well')
        field = subconfig.get(subconfig_keys[-1],None)
        if field is None:
            if default is _sentinel:
                raise Exception(f'No field found for keys {subconfig_keys} in config {config_or_config_name}, and no default value provided')
            else:
                return default
        return field
    

    def fetch_class_from_config(self,config_or_config_name,subconfig_keys,default=_sentinel):
        model_class = self.fetch_config_field(config_or_config_name, subconfig_keys=subconfig_keys,default=None)
        if model_class is None:
            if default is _sentinel:
                raise Exception(f'No class found for keys {subconfig_keys} in config {config_or_config_name}')
            else:
                return default
        return self.fetch_class(model_class)

    def fetch_class(self,model_class):
        return self.class_handler._locate_class(model_class)

    def load_data(self,datatype, data_args={}):
        data_path = self.get_data_path(datatype,data_args)
        if not self._is_file_present_core(data_path):
            raise Exception(f'File not found: {data_path} for datatype {datatype.__name__}')
        return self._load_data_core(datatype, data_path,data_args)
    
    def _load_data_core(self,datatype, data_path,data_args):
        if self._can_print_debug_message(datatype):
            file_size = get_file_size(data_path)
            print(f'Loading data from {data_path} ({datatype.__name__}, {file_size})')
        load_function = self.load_function_dict[datatype.FILE_DATATYPE]

        signature = inspect.signature(load_function)
        if 'data_args' in signature.parameters:
            data_args[SpecialDataArgs.DATA_TYPE] = datatype
            data = load_function(data_path, data_args)
        else:
            data = load_function(data_path)
        return data
    
    def save_data(self,datatype, data_args):
        data_path = self.get_data_path(datatype,data_args)
        self.create_directory(data_path)
        save_function = self.save_function_dict[datatype.FILE_DATATYPE]
        data = data_args[AbstractDatatype.DATA]
        try: 
            save_function(data,data_path)
            if self._can_print_debug_message(datatype):
                file_size = get_file_size(data_path)
                print(f'Saved data to {data_path} ({datatype.__name__}, {file_size})')

        except Exception as e:
            print(f'Attempted to save data to {data_path} ({datatype.__name__}):')
            raise e
            
        self._extend_group_permissions(data_path,datatype=datatype)

    def create_directory(self,path):
        dir_path = os.path.dirname(path)
        if len(dir_path) == 0:
            return
        
        if not os.path.exists(dir_path):
            if self.is_debug:
                print(f'Creating directory: {dir_path}')
            os.makedirs(dir_path)
            self._extend_group_permissions(dir_path)


    def transfer_data(self,source_datatype,target_datatype, source_data_args, target_data_args):
        source_path = self.get_data_path(source_datatype, data_args=source_data_args)
        target_path = self.get_data_path(target_datatype, data_args=target_data_args)
        self.create_directory(target_path)
        if self.is_debug:
            print(f'Overwriting {target_path} with data at {source_path}')
        shutil.copy(source_path, target_path)



    def delete_data(self,datatype, data_args):
        for file_path in self.get_file_iterator(datatype, data_args = data_args):
            if os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path, topdown=False):
                    for name in files:
                        full_path = os.path.join(root, name)
                        if self.is_debug:
                            file_size= get_file_size(full_path)
                            print(f'Deleting file: {full_path} ({datatype.__name__}, {file_size})')
                        os.remove(full_path)
                    for name in dirs:
                        full_dir_path = os.path.join(root, name)
                        os.rmdir(full_dir_path)
                os.rmdir(file_path)
            else:
                os.remove(file_path)

    def get_data_path(self,datatype,data_args={},is_lock_file=False, is_from=None, is_to=None):

        #Build the relative path
        relative_path_list = self._build_relative_path_list(datatype,data_args)
        if datatype.FILE_DATATYPE is not FileDatatypes.EMPTY:
            if datatype.FILE_DATATYPE not in self.file_extension_dict:
                raise Exception(f'File datatype {datatype.FILE_DATATYPE.value} not found in file extension dict. Please check the supported filetypes in the system config.')
            file_extenion = self.file_extension_dict[datatype.FILE_DATATYPE]
            relative_path_list[-1] += f'.{file_extenion}'
        
        if is_lock_file:
            relative_path_list[-1] += '.lock'


        if datatype.USE_ONLY_RELATIVE_PATH:
            complete_path = os.path.join(*relative_path_list)
        else:
            path_prefix = self._get_path_prefix(datatype, is_from, is_to)
            complete_path =  os.path.join( *path_prefix, *relative_path_list)
            if not complete_path.startswith(os.sep):
                complete_path = os.sep + complete_path
            complete_path = self._resolve_symlinks(complete_path,datatype)
            complete_path = os.path.normpath(complete_path)

        return complete_path
    

    def _resolve_symlinks(self, path,datatype):
        if self.system_transfer is None:
            return path
        if self._can_print_debug_message(datatype):
            print(f'Due to system transfer, resolving symlinks for path: {path}')
        symlink_set = set()
        path = self._resolve_symlinks_recursive(path,symlink_set,datatype)
        return path


    def _resolve_symlinks_recursive(self,path,symlink_set,datatype):
        path_components = path.split(os.sep)
        #for i in range(len(path_components)-1):
        for i in range(len(path_components)):
            partial_path = '/'+ os.path.join(*path_components[:i+1])
            if os.path.islink(partial_path):
                if partial_path in symlink_set:
                    raise Exception(f'Cycle detected in symlinks: {partial_path} already visited')
                symlink_set.add(partial_path)


                symlink_target = os.readlink(partial_path)
                if self._can_print_debug_message(datatype):
                    print(f'Found symlink: {partial_path} to {symlink_target}')

                transfer_system_base_directory = self.system_config.get(
                    SpecialDataArgs.SYSTEM_PATHS.value, {}).get(
                    self.system_transfer, {}).get(
                    self.PROJECT_BASE_DIRECTORY, None)
                if os.path.isabs(symlink_target):
                    relative_path = os.path.relpath(symlink_target, start=transfer_system_base_directory)
                    unsymlinked_path = os.path.join(*self.absolute_path_prefix,relative_path,*path_components[i+1:])
                    #TODO: See if this code can be consolidated with the other use case'
                else:
                    unsymlinked_path = os.path.normpath(os.path.join(*path_components[:i], symlink_target, *path_components[i+1:]))

                if not unsymlinked_path.startswith(os.sep):
                    unsymlinked_path = os.sep + unsymlinked_path
                return self._resolve_symlinks_recursive(unsymlinked_path, symlink_set,datatype)

        return path



    def _get_path_prefix(self,datatype,is_from, is_to):
        if datatype is Config:
            return os.getcwd().split(os.sep) #Config is always assumed to be in the current working directory
        prefix = self.absolute_path_prefix

        if (is_from is not None) and (is_to is not None):
            raise Exception('cannot specify both is_from and is_to')
        elif (is_from is not None) or (is_to is not None):
            shortest_path = self.get_entry_point_path(is_from,is_to)
            prefix += shortest_path.split(os.sep)

        return prefix
    
    def atomic_operation(self,datatype,data_args,atomic_function,new_data):
        data_lock_path = self.get_data_path(datatype, data_args=data_args,is_lock_file=True)
        if self.is_debug:
            print(f'Creating filelock at {data_lock_path}')
        timeout = self.system_config.get(self.FILELOCK_TIMEOUT_KEY, 60)
        filelock = FileLock(data_lock_path, timeout=timeout)
        filelock.acquire()
        if self.is_file_present(datatype, data_args=data_args):
            data = self.load_data(datatype,data_args=data_args)
        else:
            data = None
        modified_data = atomic_function(data,new_data)
        data_args[AbstractDatatype.DATA] = modified_data
        self.save_data(datatype, data_args)

        os.remove(data_lock_path)
        filelock.release()
        if self.is_debug:
            print(f'Released and deleted filelock at {data_lock_path}')
        

    def get_file_iterator(self, datatype, data_args, can_return_data_args= False, selected_indices=None):
        partial_path = self.get_data_path(datatype,data_args)
        if self._can_print_debug_message(datatype):
            print(f'Getting file iterator for partial path: {partial_path}')

        for idx, file in enumerate(sorted(glob.glob(partial_path,recursive=True))):
            if selected_indices is not None:
                if idx not in selected_indices:
                    continue
            if can_return_data_args:
                relative_path_tuple = os.path.relpath(file, self.PROJECT_BASE_DIRECTORY).split(os.sep)
                relative_path_tuple[-1] = relative_path_tuple[-1].split('.')[0]  # Remove file extension
                relative_path_tuple = tuple(relative_path_tuple)

                if hasattr(datatype, '_retrieve_data_args'):
                    data_args[SpecialDataArgs.DATA_IO]=self
                    data_args[SpecialDataArgs.DATA_TYPE]=datatype
                    file_specific_data_args = datatype._retrieve_data_args(relative_path_tuple, data_args)
                else:
                    raise Exception(f'Datatype {datatype} does not have a _retrieve_data_args method. Please implement it to retrieve data args from the file path.')
                yield file, file_specific_data_args
            else:
                yield file


    def get_file_count(self, datatype, data_args):
        count = 0
        for _ in self.get_file_iterator(datatype, data_args):
            count += 1
        return count


    def get_data_iterator(self, data_type, data_args,can_return_data_args=False,selected_indices=None):

        if can_return_data_args:
            for file_path, data_args in self.get_file_iterator(data_type, data_args, can_return_data_args,selected_indices):
                data = self._load_data_core(data_type, file_path, data_args)
                yield data, data_args
        else:
            for file_path in self.get_file_iterator(data_type, data_args,can_return_data_args,selected_indices):
                data = self._load_data_core(data_type, file_path, data_args)
                yield data

    def _build_relative_path_list(self,datatype,data_args):
        relative_path_list = []
        for entry in datatype.RELATIVE_PATH_TUPLE:
            if entry == FilePathEntries.BASE_DATA_DIRECTORY:
                relative_path_list.append(self.base_data_directory_name)
            elif entry == FilePathEntries.IDX_ENTRY:
                idx = data_args[AbstractDatatype.IDX]
                if idx == FilePathEntries.OPEN_ENTRY:
                    relative_path_list.append('**')
                else:
                    relative_path_list.append(str(idx))
            elif entry == FilePathEntries.MODULATED_IDX_ENTRY:
                max_idx = self.system_config.get(self.MAX_INDEXED_DIRECTORY_SIZE, 10000)
                raise Exception('Modulated idx entry is not implemented yet')
            elif entry == FilePathEntries.CONFIG_ENTRY:
                config_name = data_args[AbstractDatatype.CONFIG_NAME]
                if config_name is None:
                    raise Exception(f'Config name not found in data args: {data_args}')
                if config_name == FilePathEntries.OPEN_ENTRY:
                    relative_path_list.append('**')
                else:
                    relative_config_tuple = self._config_to_tuple_fn(config_name)
                    relative_path_list.extend(relative_config_tuple)
            elif entry == FilePathEntries.TIMESTAMP_CONFIG_ENTRY:
                config_name = data_args[AbstractDatatype.CONFIG_NAME]
                if config_name is None:
                    raise Exception(f'Config name not found in data args: {data_args}')
                
                if config_name == FilePathEntries.OPEN_ENTRY:
                    config_string = '*'
                else:
                    relative_config_tuple = self._config_to_tuple_fn(config_name)
                    config_string = relative_config_tuple[-1]
                
                if AbstractDatatype.TIMESTAMP in data_args:
                    timestamp = data_args[AbstractDatatype.TIMESTAMP]
                    if timestamp == FilePathEntries.OPEN_ENTRY:
                        timestamp = '*'
                else:
                    timestamp = self._get_timestamp()

                relative_path_list.append(f'{config_string}_{timestamp}')
            elif entry == FilePathEntries.DATA_TYPE_ENTRY:
                data_type_entry = datatype.__class__.__name__
                relative_path_list.append(data_type_entry)
            elif isinstance(entry, dict):
                if len(entry) != 1:
                    raise Exception(f'Dictionary entry in RELATIVE_PATH_TUPLE must have exactly one key-value pair, but got: {entry}')
                key, value = next(iter(entry.items()))
                if key == FilePathEntries.DATA_ARG_ENTRY:
                    field = data_args[value]
                    if field == FilePathEntries.OPEN_ENTRY:
                        relative_path_list.append('*')
                    else:
                        relative_path_list.append(str(field))
                elif key == FilePathEntries.CUSTOM_LOGIC:
                    custom_fn = getattr(datatype,value)
                    data_args[SpecialDataArgs.DATA_IO]=self
                    data_args[SpecialDataArgs.DATA_TYPE]=datatype
                    custom_values = custom_fn(data_args)

                    if custom_values is FilePathEntries.OPEN_ENTRY:
                        custom_values = ['*']
                    if isinstance(custom_values, str):
                        custom_values = [custom_values]

                    if custom_values is not None:
                        relative_path_list.extend(custom_values)
                elif key == FilePathEntries.ATTRIBUTE_ENTRY:
                    attribute = getattr(datatype,value)
                    relative_path_list.append(str(attribute))
                elif key == FilePathEntries.ZERO_PADDED_IDX_ENTRY:
                    idx = data_args[AbstractDatatype.IDX]
                    if idx == FilePathEntries.OPEN_ENTRY:
                        relative_path_list.append('*')
                    else:
                        zero_padded_idx = str(idx).zfill(value)
                        relative_path_list.append(zero_padded_idx)
                else:
                    raise Exception(f'Invalid key in dictionary entry in RELATIVE_PATH_TUPLE: {key}')
            elif isinstance(entry, str):
                relative_path_list.append(entry)
            else:
                raise Exception(f'Invalid entry in RELATIVE_PATH_TUPLE: {entry}')
        return relative_path_list


    # TODO: Deprecate
    # def get_datatype_length(self,datatype, data_args={}):
    #     if datatype in self.lengths_cache:
    #         length = self.lengths_cache[datatype]
    #     else:
    #         if datatype.LENGTH == -1:
    #             data_args[SpecialDataArgs.DATA_IO]=self
    #             data_args[SpecialDataArgs.DATA_TYPE]=datatype
    #             length = datatype._custom_length_logic(data_args)
    #         else:
    #             length = datatype.LENGTH
    #         self.lengths_cache[datatype] = length
    #     return length    

        
    def _get_config_directory(self):
        config_directory_key = 'config_directory'
        if config_directory_key in self.system_config:
            return self.system_config[config_directory_key]
        else:
            raise Exception(f'{config_directory_key} found in system config ({self.system_config_path})')
    
    def is_file_present(self,datatype,data_args):
        data_path = self.get_data_path(datatype,data_args)
        if self._can_print_debug_message(datatype):
            print('Checking if file is present at',data_path)
        is_file_present = self._is_file_present_core(data_path)
        return is_file_present
    
    def _is_file_present_core(self,data_path):
        return os.path.exists(data_path)
    

    def run_system_command(self,command,return_output=False, return_exit_code=False):
        if self.is_debug:
            print('Running terminal command:',command)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            shell=True)
        all_lines = []
        for line in process.stdout:
            print(line, end='')
            if return_output:
                all_lines.append(line.strip())
        
        process.wait()
        if return_exit_code and return_output:
            return all_lines, process.returncode
        elif return_output:
            return all_lines
        elif return_exit_code:
            return process.returncode

    def execute_python_command(self,entry_point_name, args_dict):
        cd_path = self.get_entry_point_path(is_to=entry_point_name)
        conda_path = self.get_conda_path(entry_point_name)
        python_entry_file = self.system_config.get(
            SpecialDataArgs.SYSTEM_PATHS.value, {}).get(
            self.system_identity, {}).get(
            SpecialDataArgs.EXTERNAL_CALLS.value, {}).get(
            entry_point_name, {}).get(
            SpecialDataArgs.PYTHON_ENTRY_POINT.value, None)
        if python_entry_file is None:
            raise Exception(f'Python entry point for {entry_point_name} not found in system config for system identity {self.system_identity}')
        args_string = ''
        for key, value in args_dict.items():
            if value is None:
                args_string += f' --{key}'
            else:
                args_string += f' --{key} {value}'
        cmmd_string = (
            f'cd {cd_path} && {conda_path} {python_entry_file}.py {args_string}'
        )
        self.run_system_command(cmmd_string)


    def get_base_conda_name(self):
        conda_name = self.system_config.get(
            SpecialDataArgs.SYSTEM_PATHS.value, {}).get(
            self.system_identity, {}).get(
            self.BASE_CONDA_NAME, None)
        if conda_name is None:
            raise Exception(f'Base conda name not found in system config for system identity {self.system_identity}')
        return conda_name

    def get_conda_path(self,entry_point_name):
        conda_path = self.system_config.get(
            SpecialDataArgs.SYSTEM_PATHS.value, {}).get(
            self.system_identity, {}).get(
            SpecialDataArgs.EXTERNAL_CALLS.value, {}).get(
            entry_point_name, {}).get(
            SpecialDataArgs.CONDA_PATH.value, None)
        
        conda_path = os.path.join(conda_path, 'bin', 'python')
        if conda_path is None:
            raise Exception(f'Conda path {entry_point_name} not found in system config for system identity {self.system_identity}')
        return conda_path
    
    def get_entry_point_path(self,is_from=None, is_to=None):
        #TODO: Should deprecate in favor of using absolute paths 
        if (is_from is not None) and (is_to is not None):
            raise Exception('cannot specify both is_from and is_to')
        elif is_from is None and is_to is None:
            raise Exception('must specify either is_from or is_to')
        
        entry_point_name = is_from if is_from is not None else is_to
        entry_point_path = self.system_config.get(
            SpecialDataArgs.SYSTEM_PATHS.value, {}).get(
            self.system_identity, {}).get(
            SpecialDataArgs.EXTERNAL_CALLS.value, {}).get(
            entry_point_name, {}).get(
            SpecialDataArgs.ENTRY_POINT.value, None)
        
        if entry_point_path is None:
            raise Exception(f'Entry point {entry_point_name} not found in system config for system identity {self.system_identity}')
        
        cwd = os.getcwd()
        if is_to is not None:
            relpath = os.path.relpath(entry_point_path, cwd)
        else:
            relpath = os.path.relpath(cwd, entry_point_path)
        

        return relpath
    
    def _config_to_tuple_fn(self,config_path):
        cwd = os.getcwd()
        base_cwd = os.path.basename(cwd)
        path_parts = config_path.split(os.sep)
        indices = [i for i, part in enumerate(path_parts) if part == base_cwd]

        if len(indices) > 1:
            print(f'WARNING: config path: {config_path} has multiple instances of {base_cwd}. This may cause issues with config loading.'
                    'It is strongly recommended to have only one instance of the base directory name in the config path.')
        elif len(indices) == 1:                
            path_parts = path_parts[indices[-1]+1:]
        config_file_extension = f'.{self.file_extension_dict[FileDatatypes.OMEGA_CONF]}'
        if path_parts[-1].endswith(config_file_extension):
            path_parts[-1] = path_parts[-1][:-len(config_file_extension)]
        return tuple(path_parts)
    
    def find_import(self,class_name):
        full_class = self.fetch_class(class_name)
        if full_class is None:
            raise Exception(f'Class {class_name} not found in project')
        module = full_class.__module__
        print(f'from {module} import {class_name}')

    
    def _get_timestamp(self):
        return datetime.now().strftime(self.timestamp_format)
    
    def _get_timestamp_format_size(self):
        return _calculate_timestamp_length(self.timestamp_format)


    def load_file_extension_dicts(self):
        aux_file_fn = self.system_config.get(self.AUX_FILETYPES_FN, None)

        self.load_function_dict, \
        self.save_function_dict, \
        self.file_extension_dict = _initialize_load_save_extension_dicts(self.system_config.get(SpecialDataArgs.SUPPORTED_FILETYPES.value, []),aux_file_fn)


    def load_absolute_path_prefix(self):
        system_paths_dict = self.system_config.get(SpecialDataArgs.SYSTEM_PATHS.value, {}).get(self.system_identity,{})
        if self.system_transfer is None:
            self.absolute_path_prefix = system_paths_dict.get(self.PROJECT_BASE_DIRECTORY, None)
        else: 
            self.absolute_path_prefix = system_paths_dict.get(self.SYSTEM_TRANSFERS,{}).get(self.system_transfer,None)
        
        if self.absolute_path_prefix is None:
            if self.system_transfer is None:
                raise Exception(f'Base data directory not found in system config for system identity {self.system_identity}. Please specify it under {SpecialDataArgs.SYSTEM_PATHS.value}:{self.system_identity}:{self.PROJECT_BASE_DIRECTORY}')
            else:
                raise Exception(f'Base data directory not found in system config for transfer {self.system_identity} to {self.system_transfer}. Please specify it under {SpecialDataArgs.SYSTEM_PATHS.value}:{self.system_identity}:{self.SYSTEM_TRANSFERS}:{self.system_transfer}:{self.system_transfer}')

        self.absolute_path_prefix = self.absolute_path_prefix.split(os.sep)


    def load_system_identity(self):
        system_identity_file = self.system_config.get(self.SYSTEM_IDENTITY_FILE, '.system_identity.txt')
        with open(system_identity_file, 'r') as system_identity_file:
            self.system_identity = system_identity_file.read().strip()
        if self.is_debug:
            print(f'System Identity: {self.system_identity}')


    def load_can_add_group_permissions_on_save(self):
        local_system_paths_dict = self._get_local_system_paths_dict()
        self.can_add_group_permissions_on_save = local_system_paths_dict.get(self.CAN_ADD_GROUP_PERMISSIONS_ON_SAVE, False)
    
    def get_slurm_server_credentials_and_project_directory(self):
        local_system_paths_dict = self._get_local_system_paths_dict()
        slurm_server_credentials = local_system_paths_dict.get(self.SLURM_SERVER_CREDENTIALS, None)
        slurm_project_directory = local_system_paths_dict.get(self.SLURM_PROJECT_DIRECTORY, None)
        return slurm_server_credentials, slurm_project_directory

    def _get_local_system_paths_dict(self):
        all_system_paths_dict = self.system_config.get(SpecialDataArgs.SYSTEM_PATHS.value, {})
        if self.system_transfer is None:
            local_system_paths_dict = all_system_paths_dict.get(self.system_identity, {})
        else:
            local_system_paths_dict = all_system_paths_dict.get(self.system_transfer, {})
        if local_system_paths_dict is None:
            raise Exception(f'No system paths found for system identity {self.system_identity} in system config. Please specify it under {SpecialDataArgs.SYSTEM_PATHS.value}:{self.system_identity}')
        return local_system_paths_dict
            
    def _extend_group_permissions(self, data_path,datatype=None):
        permissions = os.stat(data_path).st_mode

        is_executable_file = False
        if (datatype is not None) and hasattr(datatype, 'IS_EXECUTABLE') and datatype.IS_EXECUTABLE:
            is_executable_file = True

        if is_executable_file:
            # Add executable permissions for the user
            permissions = permissions | stat.S_IXUSR

        if self.can_add_group_permissions_on_save:            
            #Allow write permissions for the group (both for directories and files)
            permissions = permissions | stat.S_IWGRP

            if is_executable_file:
                permissions = permissions | stat.S_IXGRP

        os.chmod(data_path, permissions)

        #Recursively call permissions
        if os.path.isdir(data_path):
            for root, dirs, files in os.walk(data_path):
                for name in files:
                    file_path = os.path.join(root, name)
                    self._extend_group_permissions(file_path,datatype)
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    self._extend_group_permissions(dir_path,datatype)


    def _can_print_debug_message(self, datatype):
        if not self.is_debug:
            return False
        if datatype in self.no_print_on_debug_set:
            return False
        if not datatype.CAN_PRINT_ON_DEBUG:
            print(f'File I/O is occuring on datatype {datatype.__name__}. All debug messages for this datatype will be suppressed as CAN_PRINT_ON_DEBUG=False.')
            self.no_print_on_debug_set.add(datatype)
            return False
        return True
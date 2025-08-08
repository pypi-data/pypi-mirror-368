from file_golem.file_datatypes import FileDatatypes, FilePathEntries, AbstractDatatype

class Config(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.OMEGA_CONF
    GRID_IDX = 'grid_idx'
    GRID_IDX_LABELS = 'grid_idx_labels'
    USE_ONLY_RELATIVE_PATH = True  # Ony use relative paths for configuration files

    RELATIVE_PATH_TUPLE = (
        FilePathEntries.CONFIG_ENTRY,
        {FilePathEntries.CUSTOM_LOGIC: '_grid_search_suffix'}
    )
    
    @staticmethod
    def _grid_search_suffix(data_args):
        if not (Config.GRID_IDX in data_args):
            return ()

        grid_idx = data_args[Config.GRID_IDX]
        if not (Config.GRID_IDX_LABELS in data_args):
            idx = '_'.join(map(str, grid_idx))
            return tuple([idx])

        grid_idx_labels = data_args[Config.GRID_IDX_LABELS]
        formatted_parameters = []
        for parameter_num, parameter_index in enumerate(grid_idx):
            formatted_parameter = Config._get_parameter_for_config_name(grid_idx_labels,parameter_num,parameter_index)
            formatted_parameters.append(formatted_parameter)

        complete_string = '_'.join(formatted_parameters)
        return tuple([complete_string])

    #TODO: Current config name logic causes issues with multi step grid searches when referencing prior configs. 
    @staticmethod
    def _get_parameter_for_config_name(grid_idx_labels, parameter_num, parameter_index):
        parameter_key = list(grid_idx_labels.keys())[parameter_num]
        parameter_string = parameter_key[0].split('.')[-1]
        parameter_value = grid_idx_labels[parameter_key][parameter_index][0]
        # Check if it is a config
        if isinstance(parameter_value, str) and ('/' in parameter_value):
            parameter_value = parameter_value.split('/')[-1]
            if parameter_value.endswith('.yaml'):
                parameter_value = parameter_value[:-5]
        formatted_parameter = f'{parameter_string}:{parameter_value}'
        return formatted_parameter

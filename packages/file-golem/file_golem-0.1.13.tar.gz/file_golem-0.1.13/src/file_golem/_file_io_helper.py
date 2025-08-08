import os
from file_golem.file_datatypes import FileDatatypes, SpecialDataArgs
import importlib


def get_file_size(file_path):
    file_size = os.path.getsize(file_path)
    """
    Formats the file size into KB, MB, or GB.
    """
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if file_size < 1024:
            formatted_size = f"{file_size:.2f} {unit}"
            break
        file_size /= 1024

    return formatted_size

def _initialize_load_save_extension_dicts(supported_datatypes,aux_file_function):
    if aux_file_function is None:
        load_function_dict = {}
        save_function_dict = {}
        file_extension_dict = {}
    else:

        function_name = aux_file_function.split('.')[-1]  # Extract the function name from the string
        module_name = '.'.join(aux_file_function.split('.')[:-1])  # Extract the module name


        module = importlib.import_module(module_name)  # Import the module
        function = getattr(module, function_name) 
        load_function_dict, save_function_dict, file_extension_dict = function()

    can_load_all = (len(supported_datatypes) == 0)

    if FileDatatypes.JPEG.value in supported_datatypes or can_load_all:
        from PIL import Image
        def _load_jpeg(path):
            with Image.open(path) as img:
                return img.convert('RGB')
            
        def _save_jpeg(data,path):
            data.save(path, format='JPEG')


        load_function_dict[FileDatatypes.JPEG] = _load_jpeg
        save_function_dict[FileDatatypes.JPEG] = _save_jpeg
        file_extension_dict[FileDatatypes.JPEG] = 'jpg'

    if FileDatatypes.JPEG_BOLD.value in supported_datatypes or can_load_all:
        from PIL import Image
        def _load_jpeg_bold(path):
            with Image.open(path) as img:
                return img.convert('RGB')
        
        def _save_jpeg_bold(data,path):
            data.save(path, format='JPEG')

        load_function_dict[FileDatatypes.JPEG_BOLD] = _load_jpeg_bold
        save_function_dict[FileDatatypes.JPEG_BOLD] = _save_jpeg_bold
        file_extension_dict[FileDatatypes.JPEG_BOLD] = 'JPEG'




    if (FileDatatypes.OMEGA_CONF.value in supported_datatypes) or can_load_all:

        from omegaconf import OmegaConf
        def _load_omega_conf(path):
            config = OmegaConf.load(path)
            return config

        def _save_omega_conf(data,path):
            OmegaConf.save(data,path)


        load_function_dict[FileDatatypes.OMEGA_CONF] = _load_omega_conf
        save_function_dict[FileDatatypes.OMEGA_CONF] = _save_omega_conf
        file_extension_dict[FileDatatypes.OMEGA_CONF] = 'yaml'

    if (FileDatatypes.MATPLOTLIB.value) in supported_datatypes or can_load_all:
        import matplotlib.pyplot as plt

        def _save_matplotlib(data,path):
            plt.savefig(path,bbox_inches='tight', pad_inches =0.0,format='pdf')

        save_function_dict[FileDatatypes.MATPLOTLIB] = _save_matplotlib
        file_extension_dict[FileDatatypes.MATPLOTLIB] = 'pdf'


    if (FileDatatypes.NUMPY.value in supported_datatypes) or can_load_all:
        import numpy as np
        def _load_np(path):
            return np.load(path)
        
        def _save_np(data,path):
            np.save(path,data)

        load_function_dict[FileDatatypes.NUMPY] = _load_np
        save_function_dict[FileDatatypes.NUMPY] = _save_np
        file_extension_dict[FileDatatypes.NUMPY] = 'npy'

    # if (FileDatatypes.WAV.value in supported_datatypes) or can_load_all:
    #     def _load_wav(path):
    #         raise Exception("WAV loading is not implemented yet.")
        
    #     def _save_wav(data,path):
    #         raise Exception("WAV saving is not implemented yet.")

    #     load_function_dict[FileDatatypes.WAV] = _load_wav
    #     save_function_dict[FileDatatypes.WAV] = _save_wav
    #     file_extension_dict[FileDatatypes.WAV] = 'wav'

    # if (FileDatatypes.MP4.value in supported_datatypes) or can_load_all:
    #     def _load_mp4(path):
    #         raise Exception("MP4 loading is not implemented yet.")
        
    #     def _save_mp4(data,path):
    #         raise Exception("MP4 saving is not implemented yet.")
        
    #     load_function_dict[FileDatatypes.MP4] = _load_mp4
    #     save_function_dict[FileDatatypes.MP4] = _save_mp4
    #     file_extension_dict[FileDatatypes.MP4] = 'mp4'


    # if (FileDatatypes.MKV.value in supported_datatypes) or can_load_all:
    #     def _load_mkv(path):
    #         raise Exception("MKV loading is not implemented yet.")
    #     def _save_mkv(data,path):
    #         raise Exception("MKV saving is not implemented yet.")
        
    #     load_function_dict[FileDatatypes.MKV] = _load_mkv
    #     save_function_dict[FileDatatypes.MKV] = _save_mkv
    #     file_extension_dict[FileDatatypes.MKV] = 'mkv'

    if (FileDatatypes.PANDAS.value in supported_datatypes) or can_load_all:
        import pandas as pd
        def _save_pd(data,path):
            data.to_csv(path)
        
        def _load_pd(path):
            return pd.read_csv(path)
        
        load_function_dict[FileDatatypes.PANDAS] = _load_pd
        save_function_dict[FileDatatypes.PANDAS] = _save_pd
        file_extension_dict[FileDatatypes.PANDAS] = 'csv'
    
    if (FileDatatypes.JSON.value in supported_datatypes) or can_load_all:
        import json
        def _load_json(path):
            with open(path, 'r') as f:
                return json.load(f)
            
        def _save_json(json_data,path):
            with open(path, 'w') as f:
                json.dump(json_data, f, indent=4)
        
        load_function_dict[FileDatatypes.JSON] = _load_json
        save_function_dict[FileDatatypes.JSON] = _save_json
        file_extension_dict[FileDatatypes.JSON] = 'json'

    if (FileDatatypes.TEXT.value in supported_datatypes) or can_load_all:
        def _load_txt(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            return content

        def _save_txt(data, file_path):
            with open(file_path, 'w') as file:
                file.write(data)

        load_function_dict[FileDatatypes.TEXT] = _load_txt
        save_function_dict[FileDatatypes.TEXT] = _save_txt
        file_extension_dict[FileDatatypes.TEXT] = 'txt'


    if (FileDatatypes.TORCH.value in supported_datatypes) or can_load_all:
        import torch
        def _save_torch(data,path):
            torch.save(data,path)
        def _load_torch(path,weights_only=False):
            #Force load onto CPU device, only move to GPU device if necessary (typically handled by the dataloader)
            # accelerator prepped dataloader will automatically move data to the correct device after collation
            return torch.load(path,weights_only=weights_only,map_location=torch.device('cpu'))
        
        load_function_dict[FileDatatypes.TORCH] = _load_torch
        save_function_dict[FileDatatypes.TORCH] = _save_torch
        file_extension_dict[FileDatatypes.TORCH] = 'pt'

    # if (FileDatatypes.TORCH.value in supported_datatypes) or can_load_all:
    #     import torch
    #     def _save_torch(data,path):
    #         torch.save(data,path)
    #     def _load_torch(path,weights_only=False):
    #         # if torch.cuda.is_available():
    #         #     return torch.load(path,weights_only=weights_only)
    #         # else:
    #         return torch.load(path,weights_only=weights_only,map_location=torch.device('cpu'))
        
    #     load_function_dict[FileDatatypes.TORCH] = _load_torch
    #     save_function_dict[FileDatatypes.TORCH] = _save_torch
    #     file_extension_dict[FileDatatypes.TORCH] = 'pt'


    if (FileDatatypes.TORCH_CHECKPOINT.value in supported_datatypes) or can_load_all:
        import torch
        def _save_torch_checkpoint(data,path):
            torch.save(data,path)
        def _load_torch_checkpoint(path,weights_only=False):
            if torch.cuda.is_available():
                return torch.load(path,weights_only=weights_only)
            else:
                return torch.load(path,weights_only=weights_only,map_location=torch.device('cpu'))
        
        load_function_dict[FileDatatypes.TORCH_CHECKPOINT] = _load_torch_checkpoint
        save_function_dict[FileDatatypes.TORCH_CHECKPOINT] = _save_torch_checkpoint
        file_extension_dict[FileDatatypes.TORCH_CHECKPOINT] = 'pt'

    if (FileDatatypes.PICKLE.value in supported_datatypes) or can_load_all:
        import pickle
        def _save_pickle(data,path):
            with open(path, 'wb') as f:
                pickle.dump(data, f)

        def _load_pickle(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
            
        load_function_dict[FileDatatypes.PICKLE] = _load_pickle
        save_function_dict[FileDatatypes.PICKLE] = _save_pickle
        file_extension_dict[FileDatatypes.PICKLE] = 'pkl'

    if (FileDatatypes.PNG.value in supported_datatypes) or can_load_all:
        from PIL import Image
        def _load_png(path):
            with Image.open(path) as img:
                return img.convert('RGB')
            #return imageio.imread(path)
        def _save_png(data,path):
            data.save(path, format='PNG')
            #imageio.imwrite(path, data)
            # with open(path, 'wb') as img_file:
            #     img_file.write(data)
        load_function_dict[FileDatatypes.PNG] = _load_png
        save_function_dict[FileDatatypes.PNG] = _save_png
        file_extension_dict[FileDatatypes.PNG] = 'png'

    # if (FileDatatypes.PDF.value in supported_datatypes) or can_load_all:
    #     import matplotlib.pyplot as plt
    #     def _save_plt_fig(path):
    #         plt.savefig(path,bbox_inches='tight', pad_inches =0.0,format='pdf')
    #         plt.close()

    #     save_function_dict[FileDatatypes.PDF] = _save_plt_fig
    #     file_extension_dict[FileDatatypes.PDF] = 'pdf'

    if (FileDatatypes.SHELL.value in supported_datatypes) or can_load_all:
        def _save_shell_script(data,path):
            with open(path, 'w') as f:
                f.write(data)
        
        save_function_dict[FileDatatypes.SHELL] = _save_shell_script
        file_extension_dict[FileDatatypes.SHELL] = 'sh'

    if (FileDatatypes.SLURM_SCRIPT.value in supported_datatypes) or can_load_all:
        def _save_slurm_script(data,path):
            with open(path, 'w') as f:
                f.write(data)
        
        save_function_dict[FileDatatypes.SLURM_SCRIPT] = _save_slurm_script
        file_extension_dict[FileDatatypes.SLURM_SCRIPT] = 'sh'

    if (FileDatatypes.SLURM_OUTPUT_STD.value in supported_datatypes) or can_load_all:
        def _load_slurm_output_std(path,data_args):
            datatype = data_args[SpecialDataArgs.DATA_TYPE]
            last_lines = data_args[datatype.LAST_LINES] if datatype.LAST_LINES in data_args else None
            if last_lines is None:
                with open(path, 'r') as file:
                    data = file.read()
            else:
                data_io = data_args[SpecialDataArgs.DATA_IO]
                tail_command = f'tail -n {last_lines} {path}'
                data = data_io.run_system_command(tail_command,return_output=True)

            return data

        file_extension_dict[FileDatatypes.SLURM_OUTPUT_STD] = 'out'
        load_function_dict[FileDatatypes.SLURM_OUTPUT_STD] = _load_slurm_output_std


        #     def _load_audio_video_mkv(path,data_args):
        # datatype = data_args[SpecialDataArgs.DATA_TYPE]
        # start_pts = data_args[datatype.START_PTS] if datatype.START_PTS in data_args else None
        # end_pts = data_args[datatype.END_PTS] if datatype.END_PTS in data_args else None

        # with warnings.catch_warnings():
        #     warnings.filterwarnings(
        #         "ignore",
        #         message="The video decoding and encoding capabilities of torchvision are deprecated from version 0.22 and will be removed in version 0.24.",
        #         category=UserWarning,
        #         module="torchvision.io._video_deprecation_warning"
        #     )
        #     if (start_pts is None) and (end_pts is None):
        #         data = torchvision.io.read_video(path,pts_unit='sec')
        #     elif (start_pts is not None) and (end_pts is not None):
        #         data = torchvision.io.read_video(path,start_pts=start_pts,end_pts=end_pts,pts_unit='sec')
        #     else:
        #         raise ValueError("Both start_pts and end_pts must be provided or neither must be provided.")

        # return data

    if (FileDatatypes.SLURM_OUTPUT_ERR.value in supported_datatypes) or can_load_all:
        def _load_slurm_output_std(path,data_args):
            datatype = data_args[SpecialDataArgs.DATA_TYPE]
            last_lines = data_args[datatype.LAST_LINES] if datatype.LAST_LINES in data_args else None
            if last_lines is None:
                with open(path, 'r') as file:
                    data = file.read()
            else:
                data_io = data_args[SpecialDataArgs.DATA_IO]
                tail_command = f'tail -n {last_lines} {path}'
                data = data_io.run_system_command(tail_command,return_output=True)

            return data
        file_extension_dict[FileDatatypes.SLURM_OUTPUT_ERR] = 'err'
        load_function_dict[FileDatatypes.SLURM_OUTPUT_ERR] = _load_slurm_output_std

    return load_function_dict,save_function_dict,file_extension_dict



def _calculate_timestamp_length(format_string):
    # Mapping of format specifiers to their lengths
    format_lengths = {
        '%Y': 4,  # Year
        '%m': 2,  # Month
        '%d': 2,  # Day
        '%H': 2,  # Hour
        '%M': 2,  # Minute
        '%S': 2,  # Second
        '%f': 6,  # Microsecond
        '%z': 5,  # UTC offset
        '%a': 3,  # Abbreviated weekday name
        '%A': None,  # Full weekday name (variable length)
        '%b': 3,  # Abbreviated month name
        '%B': None,  # Full month name (variable length)
    }

    # Initialize total length
    total_length = 0
    i = 0

    while i < len(format_string):
        if format_string[i] == '%':  # Check for format specifier
            specifier = format_string[i:i+2]
            if specifier in format_lengths:
                length = format_lengths[specifier]
                if length is None:
                    raise ValueError(f"Specifier {specifier} has variable length and cannot be calculated.")
                total_length += length
                i += 2  # Skip the specifier
            else:
                raise ValueError(f"Unknown format specifier: {specifier}")
        else:
            total_length += 1  # Count static characters
            i += 1

    return total_length
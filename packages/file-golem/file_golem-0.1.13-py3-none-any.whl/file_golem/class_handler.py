import os
import ast
import pydoc


class ClassHandler:
    def __init__(self,project_src_root,has_duplicate_module_names):
        self.class_module_dict = {}
        self.has_duplicate_module_names = has_duplicate_module_names
        if self.has_duplicate_module_names:
            return
        current_working_directory = os.getcwd()
        project_path = os.path.join(current_working_directory, project_src_root)

        """Find all classes in a Python project."""
        class_file_paths_dict = {}
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".py"):  # Only process Python files
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, current_working_directory)
                    """Find all class names in a Python file."""
                    with open(file_path, "r", encoding="utf-8") as file:
                        tree = ast.parse(file.read(), filename=file_path)

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                class_name = node.name
                                if class_name in class_file_paths_dict.keys():

                                    print(f"WARNING: Duplicate class name '{class_name}' found in file {relative_path} and {class_file_paths_dict[class_name]}")
                                    print("Duplicate class names can cause issues with module resolution.")
                                    print("Please ensure unique names across files to enable module short names.")
                                    print(f"Or, set has_duplicate_module_names to True in the system config")
                                #print(f"Found class {node.name} in file {file_path}")
                                else:
                                    class_file_paths_dict[class_name] = relative_path
                                    module_name = os.path.splitext(relative_path)[0].replace(os.sep, '.')+'.'+class_name
                                    self.class_module_dict[class_name] = module_name


    def _locate_class(self,object_class):
        if object_class in self.class_module_dict:
            object_class = self.class_module_dict[object_class]
        model_type = pydoc.locate(object_class)
        if model_type is None:
            raise Exception(f'Could not find model class {object_class}')
        return model_type



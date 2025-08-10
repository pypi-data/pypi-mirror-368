"""
ComfyUI Workflow API Generator

Generates Python code from ComfyUI object_info.json using AST manipulation.
"""

import json
import ast
import astor
import re
from typing import Dict, Any, Set, List, Union
from pathlib import Path


class WorkflowGenerator:
    """
    Generates Python workflow API from ComfyUI object_info.json
    """
    
    def __init__(self, object_info: Dict[str, Any]):
        """
        Initialize the generator with object_info.
        
        Args:
            object_info: ComfyUI object_info.json content
        """
        self.object_info = object_info
        self.primitives = {
            "INT": "int",
            "FLOAT": "float", 
            "STRING": "str",
            "BOOLEAN": "bool",
        }
    
    def normalize_node_name(self, node_name: str) -> str:
        """
        Convert a node name to a valid Python identifier.
        
        Args:
            node_name: Original node name from object_info
            
        Returns:
            Valid Python identifier
        """
        # Replace invalid characters with underscores
        # Keep alphanumeric and underscores, replace everything else with underscore
        normalized = re.sub(r'[^a-zA-Z0-9_]', '_', node_name)
        
        # Remove leading digits (Python identifiers can't start with digits)
        if normalized and normalized[0].isdigit():
            normalized = '_' + normalized
        
        # Remove consecutive underscores
        normalized = re.sub(r'_+', '_', normalized)
        
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        
        # Ensure it's not empty
        if not normalized:
            normalized = 'Node'
        
        # Ensure it's not a Python keyword
        python_keywords = {
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield'
        }
        
        if normalized in python_keywords:
            normalized = normalized + '_'
        
        return normalized
    
    def get_normalized_type(self, comfy_type: Any) -> str:
        """Convert ComfyUI type to Python type."""
        if isinstance(comfy_type, list):
            return "str"  # String enum
        
        # Handle the * type (generic/any type)
        if comfy_type == "*":
            return "AnyNodeOutput"
        
        type_ = self.primitives.get(comfy_type)
        if not type_:
            # Custom ComfyUI type - normalize it like a node name
            return self.normalize_node_name(comfy_type)
        return type_
    
    def get_return_type(self, outputs: List[str]) -> ast.expr:
        """Generate return type annotation for a method."""
        if not outputs:
            return ast.Name(id="None", ctx=ast.Load())
        
        if len(outputs) == 1:
            output_type = self.get_normalized_type(outputs[0])
            if output_type == "int":
                return ast.Name(id="IntNodeOutput", ctx=ast.Load())
            elif output_type == "str":
                return ast.Name(id="StrNodeOutput", ctx=ast.Load())
            elif output_type == "float":
                return ast.Name(id="FloatNodeOutput", ctx=ast.Load())
            elif output_type == "bool":
                return ast.Name(id="BoolNodeOutput", ctx=ast.Load())
            elif output_type == "AnyNodeOutput":
                return ast.Name(id="AnyNodeOutput", ctx=ast.Load())
            else:
                return ast.Name(id=output_type, ctx=ast.Load())
        else:
            # Multiple outputs - return tuple
            types = []
            for output in outputs:
                output_type = self.get_normalized_type(output)
                if output_type == "int":
                    types.append(ast.Name(id="IntNodeOutput", ctx=ast.Load()))
                elif output_type == "str":
                    types.append(ast.Name(id="StrNodeOutput", ctx=ast.Load()))
                elif output_type == "float":
                    types.append(ast.Name(id="FloatNodeOutput", ctx=ast.Load()))
                elif output_type == "bool":
                    types.append(ast.Name(id="BoolNodeOutput", ctx=ast.Load()))
                elif output_type == "AnyNodeOutput":
                    types.append(ast.Name(id="AnyNodeOutput", ctx=ast.Load()))
                else:
                    types.append(ast.Name(id=output_type, ctx=ast.Load()))
            
            return ast.Tuple(elts=types, ctx=ast.Load())
    
    def generate_custom_types(self) -> List[ast.ClassDef]:
        """Generate custom type classes."""
        custom_types = set()
        
        # Collect all custom types from nodes
        for node_info in self.object_info.values():
            # Input types - handle both required and optional inputs
            input_section = node_info.get("input", {})
            for input_type in ["required", "optional"]:
                if input_type in input_section:
                    for input_info in input_section[input_type].values():
                        comfy_input_type = input_info[0]
                        normalized_type = self.get_normalized_type(comfy_input_type)
                        if normalized_type not in ["int", "float", "str", "bool"]:
                            custom_types.add(normalized_type)
            
            # Output types
            for output in node_info["output"]:
                normalized_output_type = self.get_normalized_type(output)
                if normalized_output_type not in ["int", "float", "str", "bool"]:
                    custom_types.add(normalized_output_type)
        
        # Generate class definitions
        classes = []
        for type_name in sorted(custom_types):
            class_def = ast.ClassDef(
                name=type_name,
                bases=[ast.Name(id="NodeOutput", ctx=ast.Load())],
                keywords=[],
                body=[ast.Pass()],
                decorator_list=[]
            )
            classes.append(class_def)
        
        return classes
    
    def generate_node_method(self, node_name: str, node_info: Dict[str, Any]) -> ast.FunctionDef:
        """Generate a method for a single node."""
        # Convert node name to valid Python method name
        method_name = self.normalize_node_name(node_name)
        
        # Get input section
        input_section = node_info.get("input", {})
        
        # Skip nodes with no inputs (they're not useful for workflow generation)
        if not input_section:
            # Return a simple method that does nothing
            return ast.FunctionDef(
                name=method_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg="self")],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                    kwarg=None,
                    vararg=None,
                    arg_defaults=[]
                ),
                body=[
                    ast.Raise(
                        exc=ast.Call(
                            func=ast.Name(id="NotImplementedError", ctx=ast.Load()),
                            args=[ast.Constant(value=f"Node {node_name} has no inputs")],
                            keywords=[]
                        ),
                        cause=None
                    )
                ],
                decorator_list=[],
                returns=ast.Name(id="None", ctx=ast.Load())
            )
        
        # Generate arguments for both required and optional inputs
        args = []
        arg_names = []
        all_inputs = {}
        
        # Collect all inputs (required and optional)
        for input_type in ["required", "optional"]:
            if input_type in input_section:
                for input_name, input_info in input_section[input_type].items():
                    all_inputs[input_name] = input_info
        
        # Generate arguments
        for input_name, input_info in all_inputs.items():
            comfy_input_type = input_info[0]
            normalized_type = self.get_normalized_type(comfy_input_type)
            
            # Clean argument name
            clean_arg_name = self.normalize_node_name(input_name)
            arg_names.append(clean_arg_name)
            
            # Create argument
            arg = ast.arg(
                arg=clean_arg_name,
                annotation=ast.Name(id=normalized_type, ctx=ast.Load())
            )
            args.append(arg)
        
        # Generate method body
        body = []
        
        # Generate UUID
        uuid_call = ast.Assign(
            targets=[ast.Name(id="node_id", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="random_node_id", ctx=ast.Load()),
                args=[],
                keywords=[]
            )
        )
        body.append(uuid_call)
        
        # Generate node dictionary
        node_dict = ast.Assign(
            targets=[ast.Name(id="comfy_json_node", ctx=ast.Store())],
            value=ast.Dict(
                keys=[
                    ast.Constant(value="inputs"),
                    ast.Constant(value="class_type")
                ],
                values=[
                    ast.Dict(
                        keys=[ast.Constant(value=name) for name in all_inputs.keys()],
                        values=[
                            ast.Call(
                                func=ast.Name(id="to_comfy_input", ctx=ast.Load()),
                                args=[ast.Name(id=self.normalize_node_name(name), ctx=ast.Load())],
                                keywords=[]
                            ) for name in all_inputs.keys()
                        ]
                    ),
                    ast.Constant(value=node_name)
                ]
            )
        )
        body.append(node_dict)
        
        # Add node to workflow
        add_node_call = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="self", ctx=ast.Load()),
                    attr="_add_node",
                    ctx=ast.Load()
                ),
                args=[
                    ast.Name(id="node_id", ctx=ast.Load()),
                    ast.Name(id="comfy_json_node", ctx=ast.Load())
                ],
                keywords=[]
            )
        )
        body.append(add_node_call)
        
        # Generate return statement
        outputs = []
        for i, output in enumerate(node_info["output"]):
            normalized_output_type = self.get_normalized_type(output)
            
            if normalized_output_type == "int":
                actual_output_type = "IntNodeOutput"
            elif normalized_output_type == "str":
                actual_output_type = "StrNodeOutput"
            elif normalized_output_type == "float":
                actual_output_type = "FloatNodeOutput"
            elif normalized_output_type == "bool":
                actual_output_type = "BoolNodeOutput"
            else:
                actual_output_type = normalized_output_type
            
            output_obj = ast.Call(
                func=ast.Name(id=actual_output_type, ctx=ast.Load()),
                args=[
                    ast.Name(id="node_id", ctx=ast.Load()),
                    ast.Constant(value=i)
                ],
                keywords=[]
            )
            outputs.append(output_obj)
        
        if outputs:
            if len(outputs) == 1:
                return_stmt = ast.Return(value=outputs[0])
            else:
                return_stmt = ast.Return(
                    value=ast.Tuple(
                        elts=outputs,
                        ctx=ast.Load()
                    )
                )
            body.append(return_stmt)
        
        # Get return type annotation
        return_type = self.get_return_type(node_info["output"])
        
        return ast.FunctionDef(
            name=method_name,
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")] + args,
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                kwarg=None,
                vararg=None,
                arg_defaults=[]
            ),
            body=body,
            decorator_list=[],
            returns=return_type
        )
    
    def generate_workflow_class(self) -> ast.ClassDef:
        """Generate the Workflow class with all node methods."""
        # Generate node methods
        methods = []
        
        for node_name, node_info in self.object_info.items():
            method = self.generate_node_method(node_name, node_info)
            methods.append(method)
        
        # Add __init__ method
        init_method = ast.FunctionDef(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                kwarg=None,
                vararg=None,
                arg_defaults=[]
            ),
            body=[
                ast.Assign(
                    targets=[ast.Attribute(
                        value=ast.Name(id="self", ctx=ast.Load()),
                        attr="workflow_dict",
                        ctx=ast.Store()
                    )],
                    value=ast.Dict(keys=[], values=[])
                )
            ],
            decorator_list=[],
            returns=None
        )
        
        # Add _add_node method
        add_node_method = ast.FunctionDef(
            name="_add_node",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="self"),
                    ast.arg(arg="node_id"),
                    ast.arg(arg="node")
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                kwarg=None,
                vararg=None,
                arg_defaults=[]
            ),
            body=[
                ast.Assign(
                    targets=[ast.Subscript(
                        value=ast.Attribute(
                            value=ast.Name(id="self", ctx=ast.Load()),
                            attr="workflow_dict",
                            ctx=ast.Store()
                        ),
                        slice=ast.Name(id="node_id", ctx=ast.Load()),
                        ctx=ast.Store()
                    )],
                    value=ast.Name(id="node", ctx=ast.Load())
                )
            ],
            decorator_list=[],
            returns=None
        )
        
        # Add get_workflow method
        get_workflow_method = ast.FunctionDef(
            name="get_workflow",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                kwarg=None,
                vararg=None,
                arg_defaults=[]
            ),
            body=[
                ast.Return(
                    value=ast.Call(
                        func=ast.Name(id="dumps", ctx=ast.Load()),
                        args=[
                            ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr="workflow_dict",
                                ctx=ast.Load()
                            )
                        ],
                        keywords=[
                            ast.keyword(
                                arg="indent",
                                value=ast.Constant(value=2)
                            )
                        ]
                    )
                )
            ],
            decorator_list=[],
            returns=ast.Name(id="str", ctx=ast.Load())
        )
        
        return ast.ClassDef(
            name="Workflow",
            bases=[],
            keywords=[],
            body=[init_method, add_node_method, get_workflow_method] + methods,
            decorator_list=[]
        )
    
    def generate_base_classes(self) -> List[ast.ClassDef]:
        """Generate base NodeOutput classes."""
        node_output = ast.ClassDef(
            name="NodeOutput",
            bases=[],
            keywords=[],
            body=[
                ast.FunctionDef(
                    name="__init__",
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[
                            ast.arg(arg="self"),
                            ast.arg(arg="node_id"),
                            ast.arg(arg="output_index")
                        ],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                        kwarg=None,
                        vararg=None,
                        arg_defaults=[]
                    ),
                    body=[
                        ast.Assign(
                            targets=[ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr="node_id",
                                ctx=ast.Store()
                            )],
                            value=ast.Name(id="node_id", ctx=ast.Load())
                        ),
                        ast.Assign(
                            targets=[ast.Attribute(
                                value=ast.Name(id="self", ctx=ast.Load()),
                                attr="output_index",
                                ctx=ast.Store()
                            )],
                            value=ast.Name(id="output_index", ctx=ast.Load())
                        )
                    ],
                    decorator_list=[],
                    returns=None
                ),
                ast.FunctionDef(
                    name="to_input",
                    args=ast.arguments(
                        posonlyargs=[],
                        args=[ast.arg(arg="self")],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                        kwarg=None,
                        vararg=None,
                        arg_defaults=[]
                    ),
                    body=[
                        ast.Return(
                            value=ast.List(
                                elts=[
                                    ast.Attribute(
                                        value=ast.Name(id="self", ctx=ast.Load()),
                                        attr="node_id",
                                        ctx=ast.Load()
                                    ),
                                    ast.Attribute(
                                        value=ast.Name(id="self", ctx=ast.Load()),
                                        attr="output_index",
                                        ctx=ast.Load()
                                    )
                                ],
                                ctx=ast.Load()
                            )
                        )
                    ],
                    decorator_list=[],
                    returns=None
                )
            ],
            decorator_list=[]
        )
        
        # Generate specific output classes
        str_output = ast.ClassDef(
            name="StrNodeOutput",
            bases=[ast.Name(id="NodeOutput", ctx=ast.Load())],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[]
        )
        
        float_output = ast.ClassDef(
            name="FloatNodeOutput", 
            bases=[ast.Name(id="NodeOutput", ctx=ast.Load())],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[]
        )
        
        int_output = ast.ClassDef(
            name="IntNodeOutput",
            bases=[ast.Name(id="NodeOutput", ctx=ast.Load())],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[]
        )
        
        bool_output = ast.ClassDef(
            name="BoolNodeOutput",
            bases=[ast.Name(id="NodeOutput", ctx=ast.Load())],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[]
        )
        
        any_output = ast.ClassDef(
            name="AnyNodeOutput",
            bases=[ast.Name(id="NodeOutput", ctx=ast.Load())],
            keywords=[],
            body=[ast.Pass()],
            decorator_list=[]
        )
        
        return [node_output, str_output, float_output, int_output, bool_output, any_output]
    
    def generate_utility_functions(self) -> List[ast.FunctionDef]:
        """Generate utility functions."""
        to_comfy_input = ast.FunctionDef(
            name="to_comfy_input",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="value", annotation=ast.Name(id="Any", ctx=ast.Load()))
                ],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                kwarg=None,
                vararg=None,
                arg_defaults=[]
            ),
            body=[
                ast.If(
                    test=ast.Call(
                        func=ast.Name(id="isinstance", ctx=ast.Load()),
                        args=[
                            ast.Name(id="value", ctx=ast.Load()),
                            ast.Name(id="NodeOutput", ctx=ast.Load())
                        ],
                        keywords=[]
                    ),
                    body=[
                        ast.Return(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="value", ctx=ast.Load()),
                                    attr="to_input",
                                    ctx=ast.Load()
                                ),
                                args=[],
                                keywords=[]
                            )
                        )
                    ],
                    orelse=[
                        ast.Return(value=ast.Name(id="value", ctx=ast.Load()))
                    ]
                )
            ],
            decorator_list=[],
            returns=ast.Name(id="Any", ctx=ast.Load())
        )
        
        random_node_id = ast.FunctionDef(
            name="random_node_id",
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
                kwarg=None,
                vararg=None,
                arg_defaults=[]
            ),
            body=[
                ast.Return(
                    value=ast.Call(
                        func=ast.Name(id="str", ctx=ast.Load()),
                        args=[
                            ast.Call(
                                func=ast.Name(id="uuid4", ctx=ast.Load()),
                                args=[],
                                keywords=[]
                            )
                        ],
                        keywords=[]
                    )
                )
            ],
            decorator_list=[],
            returns=ast.Name(id="str", ctx=ast.Load())
        )
        
        return [to_comfy_input, random_node_id]
    
    def generate_module(self) -> ast.Module:
        """Generate the complete Python module."""
        # Imports
        imports = [
            ast.ImportFrom(
                module="uuid",
                names=[ast.alias(name="uuid4", asname=None)],
                level=0
            ),
            ast.ImportFrom(
                module="typing",
                names=[ast.alias(name="Any", asname=None)],
                level=0
            ),
            ast.ImportFrom(
                module="json",
                names=[ast.alias(name="dumps", asname=None)],
                level=0
            )
        ]
        
        # Generate all components
        utility_functions = self.generate_utility_functions()
        base_classes = self.generate_base_classes()
        custom_types = self.generate_custom_types()
        workflow_class = self.generate_workflow_class()
        
        # Combine all elements
        body = imports + utility_functions + base_classes + custom_types + [workflow_class]
        
        return ast.Module(body=body, type_ignores=[])
    
    def generate_code(self) -> str:
        """Generate Python code as a string."""
        module = self.generate_module()
        return astor.to_source(module)
    
    def save_to_file(self, output_path: str) -> None:
        """Generate code and save to file."""
        code = self.generate_code()
        
        with open(output_path, 'w') as f:
            f.write(code)
    
    @classmethod
    def from_file(cls, object_info_path: str) -> 'WorkflowGenerator':
        """Create generator from object_info.json file."""
        with open(object_info_path, 'r') as f:
            object_info = json.load(f)
        return cls(object_info)
    
    @classmethod
    def from_url(cls, url: str) -> 'WorkflowGenerator':
        """Create generator from ComfyUI server URL."""
        import requests
        response = requests.get(f"{url}/object_info")
        response.raise_for_status()
        return cls(response.json()) 
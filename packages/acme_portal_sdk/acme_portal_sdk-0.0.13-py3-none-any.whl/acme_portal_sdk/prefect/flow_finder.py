import ast
import os
import sys
import traceback
from pprint import pp
from typing import Dict, List

from acme_portal_sdk.flow_finder import FlowDetails, FlowFinder

PrefectFlowDetails = FlowDetails


class PrefectFlowFinder(FlowFinder):
    """Scans Python code directories to identify Prefect flows by analyzing decorators, extracting metadata and organizing found flows into flat list."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    class _FlowVisitor(ast.NodeVisitor):
        """AST visitor to find Prefect flow decorators in Python code."""

        def __init__(self, module: str):
            self.flows = {}
            self.current_class = None
            self.current_function = None
            self.module = module

        def visit_ClassDef(self, node):
            old_class = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = old_class

        def visit_FunctionDef(self, node):
            """Visit a function definition node."""
            self.current_function = node.name
            # Look for decorators that might be flows
            for decorator in node.decorator_list:
                if self._is_flow_decorator(decorator):
                    # Found a flow decorator
                    # Extract keyword arguments from decorator
                    kwargs = self._extract_decorator_kwargs(decorator)
                    flow_name = kwargs.get("name", self.current_function)
                    display_name = flow_name.replace("-", "_")

                    description = kwargs.get("description", "") or ast.get_docstring(
                        node
                    )
                    # Create a unique ID based on the function name and location
                    flow_key = f"{flow_name}_{id(node)}"

                    # TODO: can import_path be set from here where object is already loaded and its import path is available?
                    self.flows[flow_key] = {
                        "name": display_name,
                        "original_name": flow_name,
                        "description": description,
                        "obj_type": "function",
                        "obj_name": self.current_function,
                        "obj_parent_type": "module",
                        "obj_parent": self.module,
                        "module": self.module,
                        "id": flow_key,
                    }

                    if self.current_class:
                        self.flows[flow_key]["obj_type"] = "method"
                        self.flows[flow_key]["obj_parent"] = self.current_class
                        self.flows[flow_key]["obj_parent_type"] = "class"

                    # Debug output to help troubleshoot
                    print(f"Found flow: {display_name} (from function {flow_name})")

            self.generic_visit(node)
            self.current_function = None

        def _is_flow_decorator(self, decorator):
            """Check if a decorator is a flow decorator."""
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "flow"
            ):
                return True

            # Also check for prefect.flow or from prefect import flow
            if isinstance(decorator, ast.Call) and isinstance(
                decorator.func, ast.Attribute
            ):
                if decorator.func.attr == "flow":
                    return True

            return False

        def _extract_decorator_kwargs(self, decorator):
            """Extract keyword arguments from a decorator."""
            kwargs = {}
            if isinstance(decorator, ast.Call):
                for keyword in decorator.keywords:
                    if isinstance(keyword.value, ast.Constant):
                        kwargs[keyword.arg] = keyword.value.value
                    elif isinstance(keyword.value, ast.Str):  # For Python < 3.8
                        kwargs[keyword.arg] = keyword.value.s
            return kwargs

    def _scan_file(self, file_path: str) -> Dict[str, FlowDetails]:
        """Scan a single Python file for flows."""
        flows = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the file
            tree = ast.parse(content)
            module = os.path.splitext(os.path.basename(file_path))[0]
            visitor = self._FlowVisitor(module)
            visitor.visit(tree)

            # Process found flows
            for key, flow_data in visitor.flows.items():
                # Add file information
                flow_data["source_path"] = file_path
                flow_data["source_relative"] = os.path.relpath(
                    file_path, start=self.root_dir
                )
                flow_data["grouping"] = flow_data["source_relative"].split(os.sep)[
                    :-1
                ]  # Grouping by directory structure
                package_name = os.path.basename(self.root_dir)
                flow_data["import_path"] = (
                    f"{package_name}.{flow_data['source_relative'].replace(os.sep, '.').replace('.py', '')}"
                )
                flow_data = FlowDetails(**flow_data)
                # Add the flow to the results
                flows[key] = flow_data

                print(f"Added flow to results: {flow_data.name}")

        except Exception as e:
            print(f"Error scanning {file_path}: {str(e)}")
            traceback.print_exc(file=sys.stderr)

        return flows

    def _scan_directory(self, root_dir: str) -> Dict[str, FlowDetails]:
        """Recursively scan a directory for Python files with flows."""
        all_flows = {}

        print(f"Scanning directory: {root_dir}")

        try:
            # todo: https://stackoverflow.com/questions/25229592/python-how-to-implement-something-like-gitignore-behavior
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        print(f"Examining file: {file_path}")
                        flows = self._scan_file(file_path)
                        if flows:
                            print(f"Found {len(flows)} flows in {file_path}")
                        all_flows.update(flows)
        except Exception as e:
            print(f"Error walking directory {root_dir}: {str(e)}")
            traceback.print_exc(file=sys.stderr)

        return all_flows

    def find_flows(self) -> List[FlowDetails]:
        return list(self._scan_directory(self.root_dir).values())


if __name__ == "__main__":
    a = PrefectFlowFinder("examples/flows")
    pp(a.find_flows())

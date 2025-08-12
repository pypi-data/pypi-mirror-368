from abc import ABC, abstractmethod
from wexample_helpers.const.colors import Colors
from wexample_helpers.helpers.cli import cli_make_clickable_path
import os
from typing import Dict

class AbstractDebug(ABC):
    def __init__(self):
        self.data = None
        self.cwd = os.getcwd()
        self.collect_data()
    
    @abstractmethod
    def collect_data(self) -> None:
        """Collect debug data"""
        pass
    
    @abstractmethod
    def print(self) -> None:
        """Print debug data"""
        pass
    
    def execute(self) -> None:
        """Execute the debug operation"""
        self.print()

    def _get_relative_path(self, path: str) -> str:
        """Convert absolute path to relative path if possible."""
        try:
            rel_path = os.path.relpath(path, self.cwd)
            if not rel_path.startswith("../"):
                return rel_path
        except ValueError:
            pass
        return path
        
    def _format_class_name(self, name: str, module: str, indent: str = "") -> str:
        """Format class name with module."""
        result = f"{indent}{Colors.BLUE}→ {name}{Colors.RESET}"
        if module != "__main__":
            result += f" {Colors.GREEN}({module}){Colors.RESET}"
        return result
        
    def _format_file_path(self, path: str, line: int = None, indent: str = "") -> str:
        """Format file path with optional line number."""
        rel_path = self._get_relative_path(path)
        clickable_path = cli_make_clickable_path(path, short_title=rel_path)
        line_info = f":{line}" if line is not None else ""
        return f"{indent}    {Colors.YELLOW}File: {clickable_path}{line_info}{Colors.RESET}"
        
    def _format_instance_name(self, name: str, indent: str = "") -> str:
        """Format instance name."""
        return f"{indent}{Colors.BLUE}Instance of {name}{Colors.RESET}"
        
    def _format_attributes_header(self, indent: str = "") -> str:
        """Format attributes section header."""
        return f"{indent}{Colors.BRIGHT}Instance attributes:{Colors.RESET}"

    def _get_attribute_visibility(self, name: str) -> str:
        """Get attribute visibility based on name."""
        if name.startswith('__'):
            return "private"
        elif name.startswith('_'):
            return "protected"
        return "public"

    def _format_attribute_value(self, name: str, value: Dict, indent: str = "") -> str:
        """Format attribute value in a clean YAML-like format."""
        visibility = self._get_attribute_visibility(name)
        value_type = value.get('type', 'unknown')
        
        result = [
            f"{indent}  {Colors.BRIGHT}{name}:{Colors.RESET}",
            f"{indent}    {Colors.BLUE}type:{Colors.RESET} {value_type}",
            f"{indent}    {Colors.BLUE}visibility:{Colors.RESET} {visibility}"
        ]
        
        if value_type == "property":
            if value.get("has_getter"):
                result.append(f"{indent}    {Colors.BLUE}getter:{Colors.RESET} yes")
            if value.get("has_setter"):
                result.append(f"{indent}    {Colors.BLUE}setter:{Colors.RESET} yes")
            if value.get("has_deleter"):
                result.append(f"{indent}    {Colors.BLUE}deleter:{Colors.RESET} yes")
        else:
            result.append(f"{indent}    {Colors.BLUE}value:{Colors.RESET} {Colors.GREEN}{value.get('value', '')}{Colors.RESET}")
            
        return "\n".join(result)

    def _print_data(self, data: Dict, indent: str = "") -> None:
        """Print debug data with consistent formatting."""
        if not isinstance(data, dict):
            print(f"{indent}{Colors.YELLOW}[Invalid data structure]{Colors.RESET}")
            return

        data_type = data.get("type", "unknown")
            
        if data_type == "max_depth":
            print(f"{indent}{Colors.YELLOW}[Max depth reached]{Colors.RESET}")
            return
            
        if data_type == "circular":
            print(f"{indent}{Colors.YELLOW}[Circular reference]{Colors.RESET}")
            return
            
        if data_type == "class":
            print(self._format_class_name(data['name'], data['module'], indent))
            if "source_file" in data:
                print(self._format_file_path(data['source_file'], None, indent))
                
            if "attributes" in data:
                for name, value in data["attributes"].items():
                    print(self._format_attribute_value(name, value, indent))
                    
            if "bases" in data:
                for base in data["bases"]:
                    self._print_data(base, indent + "    ")
            return
            
        if "instance_of" in data:
            print(self._format_instance_name(data['instance_of'], indent))
            if "dump_location" in data:
                location = data['dump_location']
                print(self._format_file_path(location['file'], location['line'], indent))
            
            if "class_data" in data:
                self._print_data(data["class_data"], indent + "  ")
            
            if "attributes" in data:
                print(self._format_attributes_header(indent))
                for name, value in data["attributes"].items():
                    print(self._format_attribute_value(name, value, indent))
                    
        elif "value" in data:
            print(f"{indent}{Colors.BLUE}{data['type']}{Colors.RESET}: {Colors.GREEN}{data['value']}{Colors.RESET}")
            
        elif "elements" in data:
            print(f"{indent}{Colors.BLUE}{data['type']}{Colors.RESET} ({len(data['elements'])} elements):")
            for i, element in enumerate(data["elements"]):
                print(f"{indent}  {Colors.BRIGHT}[{i}]{Colors.RESET} →")
                self._print_data(element, indent + "    ")
                
        elif "items" in data:
            print(f"{indent}{Colors.BLUE}{data['type']}{Colors.RESET} ({len(data['items'])} elements):")
            for item in data["items"]:
                print(f"{indent}  {Colors.BRIGHT}{item['key']}{Colors.RESET} →")
                self._print_data(item["value"], indent + "    ")

    def print(self) -> None:
        """Print debug data"""
        self._print_data(self.data)

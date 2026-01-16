"""
Documentation Generator - Auto-generate API docs from Python docstrings

Part of V5 Hybrid Plugin Architecture - Batch 12
Parses Python source files and generates Markdown documentation.

Features:
- Parse Python docstrings from classes and functions
- Generate Markdown API documentation
- Support for Google-style and NumPy-style docstrings
- Auto-generate docs/api/service_api.md
- Table of contents generation
- Cross-reference linking

Version: 1.0.0
"""

import os
import ast
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ParameterDoc:
    """Documentation for a function parameter"""
    name: str
    type_hint: Optional[str] = None
    description: str = ""
    default: Optional[str] = None


@dataclass
class ReturnDoc:
    """Documentation for a function return value"""
    type_hint: Optional[str] = None
    description: str = ""


@dataclass
class FunctionDoc:
    """Documentation for a function or method"""
    name: str
    docstring: str = ""
    parameters: List[ParameterDoc] = field(default_factory=list)
    returns: Optional[ReturnDoc] = None
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)
    line_number: int = 0
    
    def to_markdown(self) -> str:
        """Convert to Markdown format"""
        md = f"#### `{self.name}`\n\n"
        
        if self.is_async:
            md = f"#### `async {self.name}`\n\n"
        
        if self.docstring:
            first_line = self.docstring.split('\n')[0].strip()
            md += f"{first_line}\n\n"
        
        if self.parameters:
            md += "**Parameters:**\n\n"
            for param in self.parameters:
                type_str = f" (`{param.type_hint}`)" if param.type_hint else ""
                default_str = f" (default: `{param.default}`)" if param.default else ""
                desc = param.description or "No description"
                md += f"- `{param.name}`{type_str}: {desc}{default_str}\n"
            md += "\n"
        
        if self.returns and (self.returns.type_hint or self.returns.description):
            md += "**Returns:**\n\n"
            type_str = f"`{self.returns.type_hint}`" if self.returns.type_hint else "Unknown"
            desc = self.returns.description or "No description"
            md += f"- {type_str}: {desc}\n\n"
        
        return md


@dataclass
class ClassDoc:
    """Documentation for a class"""
    name: str
    docstring: str = ""
    methods: List[FunctionDoc] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    line_number: int = 0
    
    def to_markdown(self) -> str:
        """Convert to Markdown format"""
        md = f"### `{self.name}`\n\n"
        
        if self.base_classes:
            md += f"**Inherits from:** {', '.join(f'`{b}`' for b in self.base_classes)}\n\n"
        
        if self.docstring:
            md += f"{self.docstring}\n\n"
        
        if self.methods:
            md += "**Methods:**\n\n"
            for method in self.methods:
                if not method.name.startswith('_') or method.name == '__init__':
                    md += method.to_markdown()
        
        return md


@dataclass
class ModuleDoc:
    """Documentation for a module"""
    name: str
    path: str
    docstring: str = ""
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[FunctionDoc] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to Markdown format"""
        md = f"## {self.name}\n\n"
        md += f"**File:** `{self.path}`\n\n"
        
        if self.docstring:
            first_para = self.docstring.split('\n\n')[0].strip()
            md += f"{first_para}\n\n"
        
        if self.classes:
            for cls in self.classes:
                md += cls.to_markdown()
                md += "---\n\n"
        
        if self.functions:
            md += "### Module Functions\n\n"
            for func in self.functions:
                if not func.name.startswith('_'):
                    md += func.to_markdown()
        
        return md


class DocstringParser:
    """Parser for Python docstrings (Google-style and NumPy-style)"""
    
    SECTIONS = ['Args', 'Arguments', 'Parameters', 'Params',
                'Returns', 'Return', 'Yields', 'Yield',
                'Raises', 'Raise', 'Exceptions',
                'Examples', 'Example', 'Usage',
                'Notes', 'Note', 'Attributes', 'Attrs']
    
    def parse(self, docstring: str) -> Dict[str, Any]:
        """
        Parse docstring into structured format.
        
        Args:
            docstring: Raw docstring text
            
        Returns:
            Dictionary with parsed sections
        """
        if not docstring:
            return {"description": "", "params": [], "returns": None}
        
        lines = docstring.strip().split('\n')
        result = {
            "description": "",
            "params": [],
            "returns": None,
            "raises": [],
            "examples": []
        }
        
        current_section = "description"
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            
            section_match = None
            for section in self.SECTIONS:
                if stripped.startswith(f"{section}:") or stripped == f"{section}:":
                    section_match = section.lower()
                    break
            
            if section_match:
                if current_section == "description":
                    result["description"] = '\n'.join(current_content).strip()
                elif current_section in ["args", "arguments", "parameters", "params"]:
                    result["params"] = self._parse_params(current_content)
                elif current_section in ["returns", "return"]:
                    result["returns"] = self._parse_returns(current_content)
                
                current_section = section_match
                current_content = []
            else:
                current_content.append(line)
        
        if current_section == "description":
            result["description"] = '\n'.join(current_content).strip()
        elif current_section in ["args", "arguments", "parameters", "params"]:
            result["params"] = self._parse_params(current_content)
        elif current_section in ["returns", "return"]:
            result["returns"] = self._parse_returns(current_content)
        
        return result
    
    def _parse_params(self, lines: List[str]) -> List[ParameterDoc]:
        """Parse parameter documentation"""
        params = []
        current_param = None
        current_desc = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            param_match = re.match(r'^(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.*)$', stripped)
            
            if param_match:
                if current_param:
                    current_param.description = ' '.join(current_desc).strip()
                    params.append(current_param)
                
                name = param_match.group(1)
                type_hint = param_match.group(2)
                desc = param_match.group(3)
                
                current_param = ParameterDoc(
                    name=name,
                    type_hint=type_hint,
                    description=desc
                )
                current_desc = [desc] if desc else []
            elif current_param:
                current_desc.append(stripped)
        
        if current_param:
            current_param.description = ' '.join(current_desc).strip()
            params.append(current_param)
        
        return params
    
    def _parse_returns(self, lines: List[str]) -> Optional[ReturnDoc]:
        """Parse return documentation"""
        content = ' '.join(line.strip() for line in lines if line.strip())
        
        if not content:
            return None
        
        type_match = re.match(r'^([^:]+):\s*(.*)$', content)
        
        if type_match:
            return ReturnDoc(
                type_hint=type_match.group(1).strip(),
                description=type_match.group(2).strip()
            )
        
        return ReturnDoc(description=content)


class PythonDocExtractor:
    """Extract documentation from Python source files"""
    
    def __init__(self):
        self.parser = DocstringParser()
    
    def extract_from_file(self, file_path: str) -> ModuleDoc:
        """
        Extract documentation from a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ModuleDoc with extracted documentation
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return ModuleDoc(
                name=Path(file_path).stem,
                path=file_path,
                docstring=f"Error parsing file: {e}"
            )
        
        module_doc = ModuleDoc(
            name=Path(file_path).stem,
            path=file_path,
            docstring=ast.get_docstring(tree) or ""
        )
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_doc = self._extract_class(node)
                module_doc.classes.append(class_doc)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_doc = self._extract_function(node)
                module_doc.functions.append(func_doc)
        
        return module_doc
    
    def _extract_class(self, node: ast.ClassDef) -> ClassDoc:
        """Extract documentation from a class definition"""
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)
        
        class_doc = ClassDoc(
            name=node.name,
            docstring=ast.get_docstring(node) or "",
            base_classes=base_classes,
            line_number=node.lineno
        )
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_doc = self._extract_function(item)
                class_doc.methods.append(method_doc)
        
        return class_doc
    
    def _extract_function(self, node) -> FunctionDoc:
        """Extract documentation from a function definition"""
        is_async = isinstance(node, ast.AsyncFunctionDef)
        
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(decorator.attr)
        
        docstring = ast.get_docstring(node) or ""
        parsed = self.parser.parse(docstring)
        
        parameters = []
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            
            type_hint = None
            if arg.annotation:
                type_hint = self._get_annotation_string(arg.annotation)
            
            param_doc = next(
                (p for p in parsed.get("params", []) if p.name == arg.arg),
                None
            )
            
            parameters.append(ParameterDoc(
                name=arg.arg,
                type_hint=type_hint or (param_doc.type_hint if param_doc else None),
                description=param_doc.description if param_doc else ""
            ))
        
        defaults = node.args.defaults
        if defaults:
            offset = len(parameters) - len(defaults)
            for i, default in enumerate(defaults):
                param_idx = offset + i
                if param_idx >= 0 and param_idx < len(parameters):
                    parameters[param_idx].default = self._get_default_string(default)
        
        returns = None
        if node.returns:
            returns = ReturnDoc(
                type_hint=self._get_annotation_string(node.returns),
                description=parsed.get("returns", ReturnDoc()).description if parsed.get("returns") else ""
            )
        elif parsed.get("returns"):
            returns = parsed["returns"]
        
        return FunctionDoc(
            name=node.name,
            docstring=docstring,
            parameters=parameters,
            returns=returns,
            is_async=is_async,
            decorators=decorators,
            line_number=node.lineno
        )
    
    def _get_annotation_string(self, annotation) -> str:
        """Convert AST annotation to string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            value = self._get_annotation_string(annotation.value)
            if isinstance(annotation.slice, ast.Tuple):
                slice_str = ', '.join(
                    self._get_annotation_string(elt) for elt in annotation.slice.elts
                )
            else:
                slice_str = self._get_annotation_string(annotation.slice)
            return f"{value}[{slice_str}]"
        elif isinstance(annotation, ast.Attribute):
            if isinstance(annotation.value, ast.Name):
                return f"{annotation.value.id}.{annotation.attr}"
            return annotation.attr
        elif isinstance(annotation, ast.BinOp):
            left = self._get_annotation_string(annotation.left)
            right = self._get_annotation_string(annotation.right)
            return f"{left} | {right}"
        return "Any"
    
    def _get_default_string(self, default) -> str:
        """Convert AST default value to string"""
        if isinstance(default, ast.Constant):
            if isinstance(default.value, str):
                return f'"{default.value}"'
            return str(default.value)
        elif isinstance(default, ast.Name):
            return default.id
        elif isinstance(default, ast.List):
            return "[]"
        elif isinstance(default, ast.Dict):
            return "{}"
        return "..."


class DocGenerator:
    """
    Generate Markdown documentation from Python source files.
    
    Usage:
        generator = DocGenerator(
            source_dir="src/core/services",
            output_dir="docs/api"
        )
        
        # Generate docs for all services
        generator.generate_all()
        
        # Generate specific file
        generator.generate_file("src/core/services/order_execution_service.py")
    """
    
    def __init__(
        self,
        source_dir: str = "src",
        output_dir: str = "docs/api"
    ):
        """
        Initialize documentation generator.
        
        Args:
            source_dir: Root directory for source files
            output_dir: Directory for generated documentation
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.extractor = PythonDocExtractor()
        
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_file(self, file_path: str, output_name: Optional[str] = None) -> str:
        """
        Generate documentation for a single file.
        
        Args:
            file_path: Path to Python file
            output_name: Optional output filename (without extension)
            
        Returns:
            Path to generated documentation file
        """
        module_doc = self.extractor.extract_from_file(file_path)
        
        if output_name is None:
            output_name = module_doc.name
        
        output_path = os.path.join(self.output_dir, f"{output_name}.md")
        
        content = self._generate_header(module_doc)
        content += module_doc.to_markdown()
        content += self._generate_footer()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Generated documentation: {output_path}")
        return output_path
    
    def generate_directory(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Generate documentation for all Python files in a directory.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            List of generated documentation file paths
        """
        generated = []
        
        pattern = "**/*.py" if recursive else "*.py"
        
        for py_file in Path(directory).glob(pattern):
            if py_file.name.startswith('_') and py_file.name != '__init__.py':
                continue
            
            if py_file.name == '__init__.py':
                continue
            
            try:
                output_path = self.generate_file(str(py_file))
                generated.append(output_path)
            except Exception as e:
                logger.error(f"Failed to generate docs for {py_file}: {e}")
        
        return generated
    
    def generate_service_api_docs(self) -> str:
        """
        Generate combined service API documentation.
        
        Returns:
            Path to generated service_api.md
        """
        services_dir = os.path.join(self.source_dir, "core", "services")
        
        if not os.path.exists(services_dir):
            services_dir = os.path.join(self.source_dir, "services")
        
        if not os.path.exists(services_dir):
            logger.warning(f"Services directory not found: {services_dir}")
            return ""
        
        modules = []
        
        for py_file in sorted(Path(services_dir).glob("*.py")):
            if py_file.name.startswith('_'):
                continue
            
            try:
                module_doc = self.extractor.extract_from_file(str(py_file))
                modules.append(module_doc)
            except Exception as e:
                logger.error(f"Failed to parse {py_file}: {e}")
        
        output_path = os.path.join(self.output_dir, "service_api.md")
        
        content = self._generate_service_api_header()
        content += self._generate_toc(modules)
        
        for module in modules:
            content += module.to_markdown()
            content += "\n---\n\n"
        
        content += self._generate_footer()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Generated service API documentation: {output_path}")
        return output_path
    
    def generate_all(self) -> Dict[str, List[str]]:
        """
        Generate all documentation.
        
        Returns:
            Dictionary with generated file paths by category
        """
        results = {
            "services": [],
            "core": [],
            "utils": [],
            "telegram": []
        }
        
        service_api = self.generate_service_api_docs()
        if service_api:
            results["services"].append(service_api)
        
        core_dir = os.path.join(self.source_dir, "core")
        if os.path.exists(core_dir):
            for py_file in Path(core_dir).glob("*.py"):
                if py_file.name.startswith('_'):
                    continue
                try:
                    output = self.generate_file(str(py_file), f"core_{py_file.stem}")
                    results["core"].append(output)
                except Exception as e:
                    logger.error(f"Failed to generate docs for {py_file}: {e}")
        
        utils_dir = os.path.join(self.source_dir, "utils")
        if os.path.exists(utils_dir):
            for py_file in Path(utils_dir).glob("*.py"):
                if py_file.name.startswith('_'):
                    continue
                try:
                    output = self.generate_file(str(py_file), f"utils_{py_file.stem}")
                    results["utils"].append(output)
                except Exception as e:
                    logger.error(f"Failed to generate docs for {py_file}: {e}")
        
        return results
    
    def _generate_header(self, module: ModuleDoc) -> str:
        """Generate documentation header"""
        return f"""# {module.name} API Documentation

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source:** `{module.path}`

---

"""
    
    def _generate_service_api_header(self) -> str:
        """Generate service API documentation header"""
        return f"""# Service API Documentation

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Version:** V5 Hybrid Plugin Architecture

This document provides API documentation for all service layer components.

---

"""
    
    def _generate_toc(self, modules: List[ModuleDoc]) -> str:
        """Generate table of contents"""
        toc = "## Table of Contents\n\n"
        
        for module in modules:
            anchor = module.name.lower().replace('_', '-')
            toc += f"- [{module.name}](#{anchor})\n"
            
            for cls in module.classes:
                cls_anchor = f"{anchor}-{cls.name.lower()}"
                toc += f"  - [{cls.name}](#{cls_anchor})\n"
        
        toc += "\n---\n\n"
        return toc
    
    def _generate_footer(self) -> str:
        """Generate documentation footer"""
        return f"""
---

*Documentation auto-generated by DocGenerator v1.0.0*  
*Part of V5 Hybrid Plugin Architecture*
"""


def create_doc_generator(
    source_dir: str = "src",
    output_dir: str = "docs/api"
) -> DocGenerator:
    """
    Factory function to create DocGenerator.
    
    Args:
        source_dir: Root directory for source files
        output_dir: Directory for generated documentation
        
    Returns:
        Configured DocGenerator instance
    """
    return DocGenerator(
        source_dir=source_dir,
        output_dir=output_dir
    )


def generate_service_api_docs(
    source_dir: str = "src",
    output_dir: str = "docs/api"
) -> str:
    """
    Convenience function to generate service API documentation.
    
    Args:
        source_dir: Root directory for source files
        output_dir: Directory for generated documentation
        
    Returns:
        Path to generated service_api.md
    """
    generator = create_doc_generator(source_dir, output_dir)
    return generator.generate_service_api_docs()

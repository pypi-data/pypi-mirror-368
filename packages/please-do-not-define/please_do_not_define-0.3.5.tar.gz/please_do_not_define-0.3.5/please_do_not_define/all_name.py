# all_name.py
import ast
from typing import Dict, Tuple

class NameUsageCollector(ast.NodeVisitor):
    def __init__(self):
        self.name_locations = {}  # 存储名称及其出现位置
        self.def_locations = {}   # 专门存储名称定义位置
        self.del_locations = {}   # 专门存储删除的变量位置
    
    def _record_usage(self, name: str, node: ast.AST):
        if name not in self.name_locations:
            self.name_locations[name] = (node.lineno, node.col_offset)
    
    def _record_definition(self, name: str, node: ast.AST):
        if name not in self.def_locations:
            self.def_locations[name] = (node.lineno, node.col_offset)
            # 定义也是一种使用，所以也记录到name_locations中
            self._record_usage(name, node)
    
    def _record_deletion(self, name: str, node: ast.AST):
        if name not in self.del_locations:
            self.del_locations[name] = (node.lineno, node.col_offset)
        # 删除也是一种使用，所以也记录到name_locations中
        self._record_usage(name, node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self._record_definition(alias.name, node)
            if alias.asname:
                self._record_definition(alias.asname, node)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self._record_definition(alias.name, node)
            if alias.asname:
                self._record_definition(alias.asname, node)
        self.generic_visit(node)
    
    def visit_Name(self, node):
        # 记录所有名称使用（包括Load和Store）
        self._record_usage(node.id, node)
        
        # 如果是定义（Store），额外记录到def_locations
        if isinstance(node.ctx, ast.Store):
            self._record_definition(node.id, node)
        # 如果是删除（Del），额外记录到del_locations
        elif isinstance(node.ctx, ast.Del):
            self._record_deletion(node.id, node)
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Store):
            if isinstance(node.value, ast.Name):
                full_name = f"{node.value.id}.{node.attr}"
                self._record_definition(full_name, node)
        elif isinstance(node.ctx, ast.Del):
            if isinstance(node.value, ast.Name):
                full_name = f"{node.value.id}.{node.attr}"
                self._record_deletion(full_name, node)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self._record_definition(node.name, node)
        for arg in node.args.args:
            self._record_definition(arg.arg, node)
        if node.args.vararg:
            self._record_definition(node.args.vararg.arg, node)
        if node.args.kwarg:
            self._record_definition(node.args.kwarg.arg, node)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self._record_definition(node.name, node)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._record_definition(target.id, node)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self._record_definition(elt.id, node)
        self.generic_visit(node)
    
    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name):
            self._record_definition(node.target.id, node)
        self.generic_visit(node)
    
    def visit_Delete(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._record_deletion(target.id, target)
            elif isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name):
                    full_name = f"{target.value.id}.{target.attr}"
                    self._record_deletion(full_name, target)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self._record_deletion(elt.id, elt)
                    elif isinstance(elt, ast.Attribute):
                        if isinstance(elt.value, ast.Name):
                            full_name = f"{elt.value.id}.{elt.attr}"
                            self._record_deletion(full_name, elt)
            elif isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Name):
                    base_name = target.value.id
                    # 简单处理：只记录字典变量名，不记录具体键
                    self._record_deletion(base_name, target)
        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            self._record_usage(name, node)
        self.generic_visit(node)

    def visit_Nonlocal(self, node):
        for name in node.names:
            self._record_usage(name, node)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.name and isinstance(node.name, str):
            self._record_definition(node.name, node)
        self.generic_visit(node)

    def visit_comprehension(self, node):
        if isinstance(node.target, ast.Name):
            self._record_definition(node.target.id, node)
        elif isinstance(node.target, (ast.Tuple, ast.List)):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    self._record_definition(elt.id, elt)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self._record_definition(node.target.id, node)
        self.generic_visit(node)

def get_name_usages_with_location(code: str) -> Dict[str, Tuple[int, int]]:
    tree = ast.parse(code)
    collector = NameUsageCollector()
    collector.visit(tree)
    # 返回所有名称使用位置（包括定义、使用和删除）
    return {**collector.def_locations, **collector.name_locations, **collector.del_locations}

if __name__ == "__main__":
    code = """
from .module import *
a = 1
b = 2
def sss():
    cc = 123
    return sss

class bbb:
    def __init__(self):
        print("bbb")

def boy():
    global xx
    def boys():
        nonlocal yy

del a
del bbb
del girl
"""
    print(get_name_usages_with_location(code))

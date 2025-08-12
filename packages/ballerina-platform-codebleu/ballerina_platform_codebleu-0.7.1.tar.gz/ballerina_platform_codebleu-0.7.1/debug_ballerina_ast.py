#!/usr/bin/env python3

"""
Debug Ballerina AST structure for return statements
"""

import sys
sys.path.insert(0, '.')

def debug_ballerina_return():
    """Debug Ballerina return statement structure"""
    print("=== Ballerina Return Statement AST ===")
    
    try:
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        
        ballerina_lang = get_tree_sitter_language("ballerina")
        ballerina_parser = Parser()
        ballerina_parser.language = ballerina_lang
        
        code = """function add(int a, int b) returns int {
    return a + b;
}"""
        
        print(f"Code:\n{code}\n")
        
        tree = ballerina_parser.parse(bytes(code, 'utf8'))
        
        def print_detailed_tree(node, level=0, max_level=8):
            if level > max_level:
                return
            
            indent = "  " * level
            print(f"{indent}{node.type}")
            
            # Look for return statements specifically
            if node.type == "return_stmt":
                print(f"{indent}  >>> RETURN STATEMENT FOUND! <<<")
                for i, child in enumerate(node.children):
                    print(f"{indent}    Child {i}: {child.type}")
            
            # Look for parameter references
            if node.type == "identifier" and len(node.children) == 0:
                text = node.text.decode('utf-8')
                print(f"{indent}  >>> IDENTIFIER: '{text}' <<<")
            
            if level < max_level:
                for child in node.children:
                    print_detailed_tree(child, level + 1, max_level)
        
        print("AST Structure:")
        print_detailed_tree(tree.root_node)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def debug_python_comparison():
    """Debug Python AST for comparison"""
    print("\n=== Python Return Statement AST ===")
    
    try:
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        
        python_lang = get_tree_sitter_language("python")
        python_parser = Parser()
        python_parser.language = python_lang
        
        code = """def add(a, b):
    return a + b"""
        
        print(f"Code:\n{code}\n")
        
        tree = python_parser.parse(bytes(code, 'utf8'))
        
        def print_detailed_tree(node, level=0, max_level=6):
            if level > max_level:
                return
            
            indent = "  " * level
            print(f"{indent}{node.type}")
            
            # Look for return statements specifically
            if node.type == "return_statement":
                print(f"{indent}  >>> RETURN STATEMENT FOUND! <<<")
                for i, child in enumerate(node.children):
                    print(f"{indent}    Child {i}: {child.type}")
            
            # Look for parameter references
            if node.type == "identifier" and len(node.children) == 0:
                text = node.text.decode('utf-8')
                print(f"{indent}  >>> IDENTIFIER: '{text}' <<<")
            
            if level < max_level:
                for child in node.children:
                    print_detailed_tree(child, level + 1, max_level)
        
        print("AST Structure:")
        print_detailed_tree(tree.root_node)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ballerina_return()
    debug_python_comparison()
#!/usr/bin/env python3

"""
Debug Ballerina inner_expr structure
"""

import sys
sys.path.insert(0, '.')

def debug_ballerina_inner_expr():
    """Debug what's inside inner_expr in Ballerina return statements"""
    print("=== Ballerina inner_expr Debug ===")
    
    try:
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        
        ballerina_lang = get_tree_sitter_language("ballerina")
        ballerina_parser = Parser()
        ballerina_parser.language = ballerina_lang
        
        code = """function add(int a, int b) returns int {
    return a + b;
}"""
        
        tree = ballerina_parser.parse(bytes(code, 'utf8'))
        
        def find_and_debug_inner_expr(node, level=0):
            indent = "  " * level
            
            if node.type == "inner_expr":
                print(f"{indent}>>> FOUND inner_expr! <<<")
                print(f"{indent}Children of inner_expr:")
                for i, child in enumerate(node.children):
                    print(f"{indent}  Child {i}: {child.type}")
                    if child.type == "identifier":
                        text = child.text.decode('utf-8')
                        print(f"{indent}    Text: '{text}'")
                    # Continue deeper
                    find_and_debug_inner_expr(child, level + 2)
            elif node.type == "expression":
                print(f"{indent}>>> FOUND expression! <<<")
                print(f"{indent}Children of expression:")
                for i, child in enumerate(node.children):
                    print(f"{indent}  Child {i}: {child.type}")
                    # Continue deeper
                    find_and_debug_inner_expr(child, level + 1)
            else:
                # Continue recursively
                for child in node.children:
                    find_and_debug_inner_expr(child, level)
        
        find_and_debug_inner_expr(tree.root_node)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ballerina_inner_expr()
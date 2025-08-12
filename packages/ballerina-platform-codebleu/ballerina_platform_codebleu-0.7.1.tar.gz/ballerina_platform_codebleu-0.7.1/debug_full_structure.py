#!/usr/bin/env python3

"""
Debug complete Ballerina AST structure with identifiers
"""

import sys
sys.path.insert(0, '.')

def debug_complete_structure():
    """Debug complete structure with focus on identifiers"""
    print("=== Complete Ballerina Structure Debug ===")
    
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
        
        def print_full_tree(node, level=0, max_level=15):
            if level > max_level:
                return
            
            indent = "  " * level
            
            # Print node type
            if node.type == "identifier" and len(node.children) == 0:
                text = node.text.decode('utf-8')
                print(f"{indent}{node.type} -> '{text}' <<<< LEAF IDENTIFIER")
            elif node.type == "return_stmt":
                print(f"{indent}{node.type} <<<< RETURN STATEMENT")
            elif node.type in ["expression", "inner_expr", "primary_expr"]:
                print(f"{indent}{node.type} <<<< EXPRESSION LAYER")
            else:
                print(f"{indent}{node.type}")
            
            # Continue deeper
            for child in node.children:
                print_full_tree(child, level + 1, max_level)
        
        print_full_tree(tree.root_node)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_complete_structure()
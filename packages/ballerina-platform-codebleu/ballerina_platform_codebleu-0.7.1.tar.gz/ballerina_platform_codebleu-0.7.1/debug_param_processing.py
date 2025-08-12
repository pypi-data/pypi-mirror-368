#!/usr/bin/env python3

"""
Debug parameter processing in DFG_ballerina
"""

import sys
sys.path.insert(0, '.')

def debug_param_processing():
    """Debug if param nodes are being processed"""
    print("=== Parameter Processing Debug ===")
    
    try:
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        from codebleu.parser.DFG import DFG_ballerina
        from codebleu.parser.utils import tree_to_token_index, index_to_code_token, tree_to_variable_index
        
        ballerina_lang = get_tree_sitter_language("ballerina")
        ballerina_parser = Parser()
        ballerina_parser.language = ballerina_lang
        
        code = """function add(int a, int b) returns int {
    return a + b;
}"""
        
        tree = ballerina_parser.parse(bytes(code, 'utf8'))
        
        # Create index_to_code mapping like get_data_flow does
        tokens_index = tree_to_token_index(tree.root_node)
        code_lines = code.split("\n")
        code_tokens = [index_to_code_token(x, code_lines) for x in tokens_index]
        index_to_code = {}
        for idx, (index, code_token) in enumerate(zip(tokens_index, code_tokens)):
            index_to_code[index] = (idx, code_token)
        
        def find_param_nodes(node, level=0):
            indent = "  " * level
            if node.type == "param":
                print(f"{indent}Found param node!")
                print(f"{indent}  Processing with DFG_ballerina...")
                
                # Test DFG_ballerina on this specific param node
                dfg, states = DFG_ballerina(node, index_to_code, {})
                print(f"{indent}  DFG result: {dfg}")
                print(f"{indent}  States result: {states}")
                
                # Show children
                print(f"{indent}  Children:")
                for i, child in enumerate(node.children):
                    print(f"{indent}    Child {i}: {child.type}")
                    if child.type == "identifier":
                        text = child.text.decode('utf-8')
                        print(f"{indent}      Text: '{text}'")
                        
                        # Test tree_to_variable_index
                        indexs = tree_to_variable_index(child, index_to_code)
                        print(f"{indent}      Variable indices: {indexs}")
                        
                        for index in indexs:
                            if index in index_to_code:
                                idx, code = index_to_code[index]
                                print(f"{indent}      Index {index} -> ({idx}, '{code}')")
            
            # Continue recursively
            for child in node.children:
                find_param_nodes(child, level + 1)
        
        find_param_nodes(tree.root_node)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_param_processing()
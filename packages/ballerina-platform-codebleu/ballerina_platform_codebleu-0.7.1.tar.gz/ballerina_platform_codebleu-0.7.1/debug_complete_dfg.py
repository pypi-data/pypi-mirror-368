#!/usr/bin/env python3

"""
Debug complete DFG construction step by step
"""

import sys
sys.path.insert(0, '.')

def debug_complete_dfg():
    """Debug complete DFG construction"""
    print("=== Complete DFG Construction Debug ===")
    
    try:
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        from codebleu.parser.utils import tree_to_token_index, index_to_code_token
        
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
        
        # Create a debug version of DFG_ballerina that shows what it's doing
        def debug_dfg_ballerina(root_node, index_to_code, states, depth=0):
            indent = "  " * depth
            print(f"{indent}Processing node: {root_node.type}")
            
            from codebleu.parser.DFG import DFG_ballerina
            
            # Process normally but show intermediate results
            dfg, new_states = DFG_ballerina(root_node, index_to_code, states)
            
            if dfg:
                print(f"{indent}  DFG entries: {dfg}")
            if new_states != states:
                print(f"{indent}  New states: {new_states}")
            
            return dfg, new_states
        
        print("Processing full tree with DFG_ballerina...")
        final_dfg, final_states = debug_dfg_ballerina(tree.root_node, index_to_code, {})
        
        print(f"\nFinal DFG: {final_dfg}")
        print(f"Final states: {final_states}")
        
        # Compare with expected Python-like structure
        print(f"\nExpected structure (like Python):")
        print(f"  Parameter declarations: ('a', 4, 'comesFrom', [], []), ('b', 7, 'comesFrom', [], [])")
        print(f"  Parameter usages: ('a', 13, 'comesFrom', ['a'], [4]), ('b', 15, 'comesFrom', ['b'], [7])")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_complete_dfg()
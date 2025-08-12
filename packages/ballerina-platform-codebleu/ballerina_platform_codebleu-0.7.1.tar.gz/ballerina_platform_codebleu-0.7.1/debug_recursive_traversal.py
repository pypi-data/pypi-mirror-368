#!/usr/bin/env python3

"""
Debug the complete recursive traversal to see where parameter declarations get lost
"""

import sys
sys.path.insert(0, '.')

def debug_recursive_traversal():
    """Trace through complete DFG_ballerina recursive processing"""
    print("=== Recursive Traversal Debug ===")
    
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
        
        # Create index_to_code mapping
        tokens_index = tree_to_token_index(tree.root_node)
        code_lines = code.split("\n")
        code_tokens = [index_to_code_token(x, code_lines) for x in tokens_index]
        index_to_code = {}
        for idx, (index, code_token) in enumerate(zip(tokens_index, code_tokens)):
            index_to_code[index] = (idx, code_token)
        
        # Create a tracing version of DFG_ballerina
        def trace_dfg_ballerina(root_node, index_to_code, states, depth=0):
            from codebleu.parser.DFG import DFG_ballerina
            from codebleu.parser.utils import tree_to_variable_index
            
            indent = "  " * depth
            print(f"{indent}→ Processing: {root_node.type}")
            
            # Check the classification
            assignment = ["assign_stmt", "compound_assign_stmt", "destructuring_assign_stmt"]
            def_statement = ["local_var_decl_stmt", "local_no_init_var_decl_stmt", "param"]
            function_statement = ["function_defn", "method_defn", "remote_method_defn"]
            if_statement = ["if_else_stmt"]
            for_statement = ["foreach_stmt"]
            while_statement = ["while_stmt"]
            return_statement = ["return_stmt"]
            
            if root_node.type in def_statement:
                print(f"{indent}  ★ PARAMETER/VARIABLE DECLARATION")
            elif root_node.type in return_statement:
                print(f"{indent}  ★ RETURN STATEMENT")
            elif len(root_node.children) == 0 and root_node.type == "identifier":
                text = root_node.text.decode('utf-8')
                print(f"{indent}  ★ IDENTIFIER: '{text}'")
                if text in states:
                    print(f"{indent}    → Already in states: {states[text]}")
                else:
                    print(f"{indent}    → New identifier")
            
            # Call actual DFG_ballerina
            dfg_result, new_states = DFG_ballerina(root_node, index_to_code, states.copy())
            
            if dfg_result:
                print(f"{indent}  ✓ DFG entries: {dfg_result}")
            if new_states != states:
                print(f"{indent}  ✓ State changes: {new_states}")
            
            return dfg_result, new_states
        
        print("Starting recursive traversal...")
        final_dfg, final_states = trace_dfg_ballerina(tree.root_node, index_to_code, {})
        
        print(f"\n" + "="*50)
        print(f"FINAL RESULT:")
        print(f"DFG: {final_dfg}")
        print(f"States: {final_states}")
        
        print(f"\nAnalysis:")
        print(f"- Total DFG entries: {len(final_dfg)}")
        print(f"- Parameter declarations expected: a@4, b@7")
        print(f"- Parameter usages expected: a@13, b@15")
        
        # Check what we're missing
        expected_indices = [4, 7, 13, 15]
        actual_indices = [entry[1] for entry in final_dfg]
        missing = set(expected_indices) - set(actual_indices)
        if missing:
            print(f"- Missing indices: {missing}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_recursive_traversal()
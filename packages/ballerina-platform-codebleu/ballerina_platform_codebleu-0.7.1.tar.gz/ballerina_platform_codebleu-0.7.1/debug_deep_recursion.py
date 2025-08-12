#!/usr/bin/env python3

"""
Debug every single recursive call to see where the traversal breaks
"""

import sys
sys.path.insert(0, '.')

def debug_deep_recursion():
    """Create a custom DFG function that traces every call"""
    print("=== Deep Recursion Debug ===")
    
    try:
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        from codebleu.parser.utils import tree_to_token_index, index_to_code_token, tree_to_variable_index
        
        ballerina_lang = get_tree_sitter_language("ballerina")
        ballerina_parser = Parser()
        ballerina_parser.language = ballerina_lang
        
        code = """function add(int a, int b) returns int {
    return a + b;
}"""
        
        tree = ballerina_parser.parse(bytes(code, 'utf8'))
        
        tokens_index = tree_to_token_index(tree.root_node)
        code_lines = code.split("\n")
        code_tokens = [index_to_code_token(x, code_lines) for x in tokens_index]
        index_to_code = {}
        for idx, (index, code_token) in enumerate(zip(tokens_index, code_tokens)):
            index_to_code[index] = (idx, code_token)
        
        def custom_dfg_ballerina(root_node, index_to_code, states, depth=0):
            """Custom DFG function with full tracing"""
            assignment = ["assign_stmt", "compound_assign_stmt", "destructuring_assign_stmt"]
            def_statement = ["local_var_decl_stmt", "local_no_init_var_decl_stmt", "param"]
            function_statement = ["function_defn", "method_defn", "remote_method_defn"]
            if_statement = ["if_else_stmt"]
            for_statement = ["foreach_stmt"]
            while_statement = ["while_stmt"]
            return_statement = ["return_stmt"]
            do_first_statement = []
            
            indent = "  " * depth
            print(f"{indent}→ {root_node.type}")
            
            states = states.copy()
            
            # Check for leaf nodes (identifiers)
            if (len(root_node.children) == 0 or root_node.type in ["string_literal", "string", "character_literal"]) and root_node.type != "comment":
                if (root_node.start_point, root_node.end_point) in index_to_code:
                    idx, code = index_to_code[(root_node.start_point, root_node.end_point)]
                    print(f"{indent}  LEAF: '{code}' at index {idx}")
                    if root_node.type == code:
                        return [], states
                    elif code in states:
                        print(f"{indent}    → References existing: {states[code]}")
                        return [(code, idx, "comesFrom", [code], states[code].copy())], states
                    else:
                        if root_node.type == "identifier":
                            states[code] = [idx]
                            print(f"{indent}    → New identifier, states updated")
                        return [(code, idx, "comesFrom", [], [])], states
                else:
                    return [], states
            
            # Handle parameter declarations
            elif root_node.type in def_statement:
                print(f"{indent}  PARAMETER/VARIABLE DECLARATION")
                DFG = []
                if root_node.type == "param":
                    print(f"{indent}    Processing param node")
                    for child in root_node.children:
                        if child.type == "identifier":
                            indexs = tree_to_variable_index(child, index_to_code)
                            for index in indexs:
                                idx, code = index_to_code[index]
                                print(f"{indent}      Param: '{code}' at index {idx}")
                                DFG.append((code, idx, "comesFrom", [], []))
                                states[code] = [idx]
                return sorted(DFG, key=lambda x: x[1]), states
            
            # Handle return statements  
            elif root_node.type in return_statement:
                print(f"{indent}  RETURN STATEMENT")
                DFG = []
                for child in root_node.children:
                    temp, states = custom_dfg_ballerina(child, index_to_code, states, depth + 1)
                    DFG += temp
                return sorted(DFG, key=lambda x: x[1]), states
            
            # Handle everything else recursively
            else:
                print(f"{indent}  RECURSIVE: {len(root_node.children)} children")
                DFG = []
                
                # Process do_first_statement children first
                for child in root_node.children:
                    if child.type in do_first_statement:
                        temp, states = custom_dfg_ballerina(child, index_to_code, states, depth + 1)
                        DFG += temp
                
                # Process all other children
                for child in root_node.children:
                    if child.type not in do_first_statement:
                        temp, states = custom_dfg_ballerina(child, index_to_code, states, depth + 1)
                        DFG += temp
                
                result_dfg = sorted(DFG, key=lambda x: x[1])
                if result_dfg:
                    print(f"{indent}  → Collected DFG: {result_dfg}")
                return result_dfg, states
        
        print("Starting custom traversal...")
        final_dfg, final_states = custom_dfg_ballerina(tree.root_node, index_to_code, {})
        
        print(f"\n" + "="*60)
        print(f"FINAL CUSTOM RESULT:")
        print(f"DFG: {final_dfg}")
        print(f"States: {final_states}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_deep_recursion()
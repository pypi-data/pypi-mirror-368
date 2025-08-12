#!/usr/bin/env python3

"""
Debug DFG_ballerina function directly
"""

import sys
sys.path.insert(0, '.')

def debug_dfg_ballerina():
    """Debug DFG_ballerina function step by step"""
    print("=== DFG_ballerina Direct Debug ===")
    
    try:
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        from codebleu.parser.DFG import DFG_ballerina
        from codebleu.dataflow_match import get_data_flow
        
        ballerina_lang = get_tree_sitter_language("ballerina")
        ballerina_parser = Parser()
        ballerina_parser.language = ballerina_lang
        
        code = """function add(int a, int b) returns int {
    return a + b;
}"""
        
        print(f"Code:\n{code}\n")
        
        tree = ballerina_parser.parse(bytes(code, 'utf8'))
        
        # Create index_to_code mapping similar to what get_data_flow does
        index_to_code = {}
        
        def traverse_tree(node):
            if len(node.children) == 0:
                # Leaf node
                index_to_code[(node.start_point, node.end_point)] = (
                    node.start_point[0] * 10000 + node.start_point[1],  # idx
                    node.text.decode('utf-8')  # code
                )
            for child in node.children:
                traverse_tree(child)
        
        traverse_tree(tree.root_node)
        
        print("Index to code mapping:")
        for key, value in sorted(index_to_code.items(), key=lambda x: x[1][0]):
            print(f"  {key} -> {value}")
        
        # Call DFG_ballerina directly
        print("\nCalling DFG_ballerina on root node...")
        dfg, states = DFG_ballerina(tree.root_node, index_to_code, {})
        
        print(f"DFG result: {dfg}")
        print(f"States result: {states}")
        
        # Also test with the actual get_data_flow function
        print("\nUsing get_data_flow function...")
        parser_tuple = [ballerina_parser, DFG_ballerina]
        
        # Let's trace through get_data_flow manually to catch the exception
        try:
            tree = parser_tuple[0].parse(bytes(code, "utf8"))
            root_node = tree.root_node
            
            from codebleu.parser.utils import tree_to_token_index, index_to_code_token
            
            tokens_index = tree_to_token_index(root_node)
            code_lines = code.split("\n")
            code_tokens = [index_to_code_token(x, code_lines) for x in tokens_index]
            index_to_code = {}
            for idx, (index, code_token) in enumerate(zip(tokens_index, code_tokens)):
                index_to_code[index] = (idx, code_token)
            
            print(f"tokens_index: {tokens_index}")
            print(f"code_tokens: {code_tokens}")
            print(f"index_to_code from get_data_flow: {index_to_code}")
            
            try:
                print("Calling DFG_ballerina from get_data_flow context...")
                DFG, states = parser_tuple[1](root_node, index_to_code, {})
                print(f"DFG from get_data_flow context: {DFG}")
            except Exception as e:
                print(f"Exception in DFG call: {e}")
                import traceback
                traceback.print_exc()
                DFG = []
            
            dfg2 = get_data_flow(code, parser_tuple)
            print(f"get_data_flow result: {dfg2}")
            
        except Exception as e:
            print(f"Exception in manual get_data_flow: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dfg_ballerina()
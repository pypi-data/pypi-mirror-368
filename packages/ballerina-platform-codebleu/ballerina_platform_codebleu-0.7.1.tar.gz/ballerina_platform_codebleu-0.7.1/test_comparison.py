#!/usr/bin/env python3

"""
Compare Python and Ballerina behavior for simple functions
"""

import sys
sys.path.insert(0, '.')

def test_python_simple():
    """Test Python simple function"""
    print("=== Python Simple Function ===")
    
    try:
        from codebleu import calc_codebleu
        
        prediction = "def add ( a , b ) :\n return a + b"
        reference = "def sum ( first , second ) :\n return second + first"
        
        print(f"Python prediction:\n{prediction}\n")
        print(f"Python reference:\n{reference}\n")
        
        result = calc_codebleu([reference], [prediction], lang="python", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
        
        print("Python Results:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"Python Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_ballerina_simple():
    """Test Ballerina simple function"""
    print("\n=== Ballerina Simple Function ===")
    
    try:
        from codebleu import calc_codebleu
        
        prediction = "function add(int a, int b) returns int {\n    return a + b;\n}"
        reference = "function sum(int first, int second) returns int {\n    return second + first;\n}"
        
        print(f"Ballerina prediction:\n{prediction}\n")
        print(f"Ballerina reference:\n{reference}\n")
        
        result = calc_codebleu([reference], [prediction], lang="ballerina", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
        
        print("Ballerina Results:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"Ballerina Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_dataflows():
    """Debug the actual dataflows being extracted"""
    print("\n=== Dataflow Debug ===")
    
    try:
        from codebleu.dataflow_match import get_data_flow
        from tree_sitter import Parser
        from codebleu.utils import get_tree_sitter_language
        from codebleu.parser.DFG import DFG_python, DFG_ballerina
        
        # Python
        print("Python dataflows:")
        python_lang = get_tree_sitter_language("python")
        python_parser = Parser()
        python_parser.language = python_lang
        python_parser_tuple = [python_parser, DFG_python]
        
        python_prediction = "def add ( a , b ) :\n return a + b"
        python_reference = "def sum ( first , second ) :\n return second + first"
        
        python_pred_dfg = get_data_flow(python_prediction, python_parser_tuple)
        python_ref_dfg = get_data_flow(python_reference, python_parser_tuple)
        
        print(f"  Python prediction DFG: {python_pred_dfg}")
        print(f"  Python reference DFG: {python_ref_dfg}")
        
        # Ballerina
        print("\nBallerina dataflows:")
        ballerina_lang = get_tree_sitter_language("ballerina")
        ballerina_parser = Parser()
        ballerina_parser.language = ballerina_lang
        ballerina_parser_tuple = [ballerina_parser, DFG_ballerina]
        
        ballerina_prediction = "function add(int a, int b) returns int {\n    return a + b;\n}"
        ballerina_reference = "function sum(int first, int second) returns int {\n    return second + first;\n}"
        
        ballerina_pred_dfg = get_data_flow(ballerina_prediction, ballerina_parser_tuple)
        ballerina_ref_dfg = get_data_flow(ballerina_reference, ballerina_parser_tuple)
        
        print(f"  Ballerina prediction DFG: {ballerina_pred_dfg}")
        print(f"  Ballerina reference DFG: {ballerina_ref_dfg}")
        
    except Exception as e:
        print(f"Debug Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Comparing Python and Ballerina Simple Function Behavior...")
    print("=" * 70)
    
    python_result = test_python_simple()
    ballerina_result = test_ballerina_simple()
    debug_dataflows()
    
    print("\n" + "=" * 70)
    print("Summary:")
    if python_result:
        print(f"Python dataflow_match_score: {python_result['dataflow_match_score']}")
    if ballerina_result:
        print(f"Ballerina dataflow_match_score: {ballerina_result['dataflow_match_score']}")
    
    if python_result and ballerina_result:
        if python_result['dataflow_match_score'] != ballerina_result['dataflow_match_score']:
            print("❌ INCONSISTENT: Python and Ballerina have different dataflow scores for equivalent simple functions!")
        else:
            print("✅ CONSISTENT: Python and Ballerina have the same dataflow behavior")
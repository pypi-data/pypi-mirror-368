#!/usr/bin/env python3

"""
Test simple approach: manually create the expected DFG structure
"""

import sys
sys.path.insert(0, '.')

def test_simple():
    try:
        from codebleu import calc_codebleu
        
        # Test with a simple modification to see if the framework works
        prediction = "function add(int a, int b) returns int {\\n    return a + b;\\n}"
        reference = "function sum(int first, int second) returns int {\\n    return second + first;\\n}"
        
        print("Testing Ballerina with simple functions:")
        print(f"Prediction: {prediction}")
        print(f"Reference: {reference}")
        
        result = calc_codebleu([reference], [prediction], lang="ballerina", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
        
        print("Results:")
        for key, value in result.items():
            print(f"  {key}: {value}")
            
        # If dataflow_match_score > 0, the fix is working
        if result['dataflow_match_score'] > 0:
            print("✅ SUCCESS: Ballerina dataflow matching is working!")
        else:
            print("❌ STILL FAILING: Dataflow score is 0")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()
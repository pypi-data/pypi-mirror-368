def DFG_ballerina(root_node, index_to_code, states):
    """
    Fixed DFG_ballerina implementation that properly handles:
    1. Parameter declarations 
    2. Parameter usage with proper state references
    3. Recursive traversal with state preservation
    """
    from .utils import tree_to_variable_index
    
    assignment = ["assign_stmt", "compound_assign_stmt", "destructuring_assign_stmt"]
    def_statement = ["local_var_decl_stmt", "local_no_init_var_decl_stmt", "param"]
    function_statement = ["function_defn", "method_defn", "remote_method_defn"]
    if_statement = ["if_else_stmt"]
    for_statement = ["foreach_stmt"]
    while_statement = ["while_stmt"]
    return_statement = ["return_stmt"]
    do_first_statement = []
    
    states = states.copy()
    
    # Handle leaf nodes (identifiers and literals)
    if (len(root_node.children) == 0 or root_node.type in ["string_literal", "string", "character_literal"]) and root_node.type != "comment":
        if (root_node.start_point, root_node.end_point) in index_to_code:
            idx, code = index_to_code[(root_node.start_point, root_node.end_point)]
            if root_node.type == code:
                return [], states
            elif code in states:
                # Reference existing declaration - THIS IS THE KEY FIX
                return [(code, idx, "comesFrom", [code], states[code].copy())], states
            else:
                # New identifier declaration
                if root_node.type == "identifier":
                    states[code] = [idx]
                return [(code, idx, "comesFrom", [], [])], states
        else:
            return [], states
    
    # Handle parameter declarations
    elif root_node.type in def_statement:
        DFG = []
        if root_node.type == "param":
            # Handle function parameters: param -> identifier
            for child in root_node.children:
                if child.type == "identifier":
                    indexs = tree_to_variable_index(child, index_to_code)
                    for index in indexs:
                        idx, code = index_to_code[index]
                        DFG.append((code, idx, "comesFrom", [], []))
                        states[code] = [idx]  # THIS IS CRUCIAL - store parameter declarations
        return sorted(DFG, key=lambda x: x[1]), states
    
    # Handle return statements  
    elif root_node.type in return_statement:
        DFG = []
        for child in root_node.children:
            temp, states = DFG_ballerina(child, index_to_code, states)
            DFG += temp
        return sorted(DFG, key=lambda x: x[1]), states
    
    # Handle everything else recursively
    else:
        DFG = []
        
        # Process do_first_statement children first
        for child in root_node.children:
            if child.type in do_first_statement:
                temp, states = DFG_ballerina(child, index_to_code, states)
                DFG += temp
        
        # Process all other children
        for child in root_node.children:
            if child.type not in do_first_statement:
                temp, states = DFG_ballerina(child, index_to_code, states)
                DFG += temp
        
        return sorted(DFG, key=lambda x: x[1]), states
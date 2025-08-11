from gpopt import Op

def format_program(individual):
    """
    Convert a postfix program into a human-readable infix expression string. 
    Input needs to be a valid postfix expression.
    """
    stack = []

    for node in individual.program:
        if node.op == Op.VAR:
            stack.append(f"VAR({int(node.value)})")
        elif node.op in {Op.ADD, Op.SUB, Op.MUL, Op.DIV}:
            if len(stack) < 2:
                return "<Invalid program>"
            b = stack.pop()
            a = stack.pop()
            op_str = {Op.ADD: "+", Op.SUB: "-", Op.MUL: "*", Op.DIV: "/"}[node.op]
            expr = f"({a} {op_str} {b})"
            stack.append(expr)
        else:
            return "<Unknown op>"
    return stack[0] if stack else "<Empty program>"

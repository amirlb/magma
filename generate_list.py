# Generate a list of equations on magmas

from itertools import permutations
from sys import stderr


EQ_SIZE = 4
VAR_NAMES = 'xyzwuv'

def generate_shapes(size):
    if size == 0:
        yield '.'
    for i in range(size):
        for left in generate_shapes(i):
            for right in generate_shapes(size - 1 - i):
                yield (left, right)

def format_shape(shape, outermost=True):
    if shape == '.':
        return '_'
    left, right = shape
    s = f'{format_shape(left, outermost=False)} ◦︎ {format_shape(right, outermost=False)}'
    if not outermost:
        return f'({s})'
    return s

def exprs_with_shape(shape, used_vars):
    if shape == '.':
        for var in range(used_vars + 1):
            yield var, max(var + 1, used_vars)
    else:
        left, right = shape
        for left_expr, used_vars in exprs_with_shape(left, used_vars):
            for right_expr, used_vars in exprs_with_shape(right, used_vars):
                yield (left_expr, right_expr), used_vars

def rename_vars(expr, perm):
    if isinstance(expr, int):
        return perm[expr]
    left, right = expr
    return (rename_vars(left, perm), rename_vars(right, perm))

def eq_symmetries_1(lhs, rhs, n_vars):
    for renaming in permutations(range(n_vars)):
        yield rename_vars(lhs, renaming), rename_vars(rhs, renaming)

def eq_symmetries(lhs, rhs, n_vars):
    for renaming in permutations(range(n_vars)):
        yield rename_vars(lhs, renaming), rename_vars(rhs, renaming)
        yield rename_vars(rhs, renaming), rename_vars(lhs, renaming)

def generate_all_eqs():
    all_eqs = set()
    for lhs_size in range(EQ_SIZE + 1):
        for lhs_shape in generate_shapes(lhs_size):
            for rhs_size in range(EQ_SIZE - lhs_size + 1):
                for rhs_shape in generate_shapes(rhs_size):
                    for lhs, used_vars in exprs_with_shape(lhs_shape, 0):
                        for rhs, all_used_vars in exprs_with_shape(rhs_shape, used_vars):
                            if all(symmetry not in all_eqs for symmetry in eq_symmetries(lhs, rhs, all_used_vars)):
                                if lhs == rhs:
                                    if not isinstance(lhs, int):
                                        continue
                                all_eqs.add((lhs, rhs))
                                yield lhs, rhs

def format_expr(expr, outermost=True):
    if isinstance(expr, int):
        return VAR_NAMES[expr]
    s = f'{format_expr(expr[0], outermost=False)} ◦︎ {format_expr(expr[1], outermost=False)}'
    if not outermost:
        return f'({s})'
    return s

print(f'Generated {len(list(generate_all_eqs()))} equations', file=stderr)

for lhs, rhs in generate_all_eqs():
    print(format_expr(lhs), '=', format_expr(rhs))

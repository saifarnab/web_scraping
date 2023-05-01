# Import the function
from pysat.solvers import Glucose3


def find_upward_closed_set(input_list):
    # Initialize the SAT solver
    solver = Glucose3()

    # Create a boolean variable for each element in the input list
    num_elements = len(input_list)
    element_vars = []
    for i in range(num_elements):
        element_vars.append(solver.new_var())

    # Add the CNF formula that encodes the upward closed set constraints
    for i in range(num_elements):
        for j in range(i + 1, num_elements):
            # If input_list[i] is not less than or equal to input_list[j],
            # then we must have either input_list[i] or input_list[j] in the upward closed set
            if input_list[i] > input_list[j]:
                solver.add_clause([-element_vars[i], -element_vars[j]])
            # If input_list[i] is less than or equal to input_list[j],
            # then we must have either input_list[i] or input_list[j] or both in the upward closed set
            else:
                solver.add_clause([element_vars[i], -element_vars[j]])
                solver.add_clause([-element_vars[i], element_vars[j]])

    # Solve the CNF formula using the SAT solver
    is_sat = solver.solve()

    if is_sat:
        # Extract the elements that belong to the upward closed set
        upward_closed_set = []
        for i in range(num_elements):
            if solver.model[element_vars[i]]:
                upward_closed_set.append(input_list[i])
        return upward_closed_set
    else:
        return None


# Example usage
input_list = [3, 6, 1, 5, 4, 2, 7, 8, 9]
upward_closed_set = find_upward_closed_set(input_list)
print("Input List:", input_list)
if upward_closed_set:
    print("Upward Closed Set of Min Terms:", upward_closed_set)
else:
    print("There is no upward closed set of min terms for the given input list.")

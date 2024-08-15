from z3 import *


# State datatypes (maybe EnumSort is better suited?)
KettleState = Datatype('Kettle')
KettleState.declare('empty')
KettleState.declare('half')
KettleState.declare('full')
KettleState = KettleState.create()

CupState = Datatype('Cup')
CupState.declare('empty')
CupState.declare('full')
CupState = CupState.create()

# Objects
Kettle = Const('Kettle', KettleState)
Cup1 = Const('Cup1', CupState)
Cup2 = Const('Cup2', CupState)

# Define the maximum number of steps
steps = 2

# Adding one for initial state in a hacky way
max_steps = steps + 1

# Define the state variables for each time step
kettle = [Const(f'Kettle_{t}', KettleState) for t in range(max_steps)]
cup1 = [Const(f'Cup1_{t}', CupState) for t in range(max_steps)]
cup2 = [Const(f'Cup2_{t}', CupState) for t in range(max_steps)]
actions = [Bool(f'Filling_{t}') for t in range(max_steps)]

# Define the solver
solver = Solver()

# Initial states
solver.add(kettle[0] == KettleState.full)
solver.add(cup1[0] == CupState.empty)
solver.add(cup2[0] == CupState.empty)

# Kettle can transition full -> half or half -> empty
def kettle_transition(k_curr, k_next):
    return Or(
        And(k_curr == KettleState.half, k_next == KettleState.empty),
        And(k_curr == KettleState.full, k_next == KettleState.half)
    )

# Cup transitions empty -> full
def cup_filling(c_curr, c_next):
    return And(c_curr == CupState.empty, c_next == CupState.full)

# Kettle transitions + either one (but only one) cup
def filling_action(kettle_curr, kettle_next, cup1_curr, cup1_next, cup2_curr, cup2_next):
    return And(
        kettle_transition(kettle_curr, kettle_next),
        Xor(
            cup_filling(cup1_curr, cup1_next),
            cup_filling(cup2_curr, cup2_next)
        )
    )

# Nothing happens, noop action
def no_action(kettle_curr, kettle_next, cup1_curr, cup1_next, cup2_curr, cup2_next):
    return And(
        kettle_next == kettle_curr,
        cup1_next == cup1_curr,
        cup2_next == cup2_curr
    )

# If actions occur - we're making a filling action; otherwise nothing happens
for t in range(max_steps-1):
    # Condition for when a filling action should occur
    filling_condition = And(
        Or(kettle[t] == KettleState.full, kettle[t] == KettleState.half),
        Or(cup1[t] == CupState.empty, cup2[t] == CupState.empty)
    )

    # If there are cups to fill & a kettle isn't empty, we imply an action
    solver.add(Implies(filling_condition,
                       actions[t]))

    # If an action occurs, it's a filling action; otherwise, no action
    solver.add(
        If(actions[t],
           filling_action(kettle[t], kettle[t+1], cup1[t], cup1[t+1], cup2[t], cup2[t+1]),
           no_action(kettle[t], kettle[t+1], cup1[t], cup1[t+1], cup2[t], cup2[t+1])
        )
    )

# Define goal state constraints: both cups are full at some step t
goal_reached = [And(cup1[t] == CupState.full, cup2[t] == CupState.full) for t in range(max_steps)]
# Goal can be reached on any step
solver.add(Or(goal_reached))

if solver.check() == sat:

    model = solver.model()
    print("Planning succeeded\n")
    steps = 0
    for t in range(max_steps):
        if model.evaluate(actions[t]) == True:
            print(f"Step {steps}:")
            print(f"Kettle: {model.evaluate(kettle[t])}")
            print(f"Cup1: {model.evaluate(cup1[t])}")
            print(f"Cup2: {model.evaluate(cup2[t])}")
            steps += 1
        if model.evaluate(goal_reached[t]):
            print(f"+ Step {steps}:")
            print(f"Kettle: {model.evaluate(kettle[t])}")
            print(f"Cup1: {model.evaluate(cup1[t])}")
            print(f"Cup2: {model.evaluate(cup2[t])}")

            break  # Exit the loop once the goal is reached
    print(f"Goal reached at step {steps}")
else:
    print("Planning failed\n")
    print(solver.unsat_core())
from z3 import *

# Object and state
Object = DeclareSort('Object')
State = DeclareSort('State')
Action = DeclareSort('Action')

# States and emptiness
stones = Function('Stones', Object, State, IntSort())

# Objects
hand = Const('hand', Object)
bag1 = Const('bag1', Object)
bag2 = Const('bag2', Object)
pile = Const('pile', Object)

# Max steps and solver instantiation
intermediate_steps = 10
s = Solver()

# Actions
pickup = Const('pickup', Action)
put_in_bag1 = Const('put_in_bag1', Action)
put_in_bag2 = Const('put_in_bag2', Action)
all_actions = [pickup, put_in_bag1, put_in_bag2]

# States
initial_state = Const('initial_state', State)
goal_state = Const('goal_state', State)
intermediate_states = [Const(f'state_{i}', State) for i in range(1, intermediate_steps + 1)]
actions = [Const(f'action_{i}', Action) for i in range(1, intermediate_steps + 1)]
all_states = [initial_state] + intermediate_states + [goal_state]
    
def bag_pile():

    # Add bag capacity constraint for all states
    for state in all_states:
        s.add(stones(bag1, state) <= IntVal(1))
        s.add(stones(bag2, state) <= IntVal(1))

    def pickup_action(current, next):
        preconditions = And(
            stones(hand, current) == IntVal(0),
            stones(pile, current) > IntVal(0)
        )
        effects = And(
            stones(pile, next) == stones(pile, current) - IntVal(1),
            stones(hand, next) == stones(hand, current) + IntVal(1),
            stones(bag1, next) == stones(bag1, current),
            stones(bag2, next) == stones(bag2, current)
        )
        return And(preconditions, effects)

    def put_in_bag_action(current, next, bag):
        preconditions = And(
            stones(hand, current) > IntVal(0),
            stones(bag, current) < IntVal(1)  # Ensure the bag has capacity
        )
        effects = And(
            stones(hand, next) == stones(hand, current) - IntVal(1),
            stones(bag, next) == stones(bag, current) + IntVal(1),
            stones(pile, next) == stones(pile, current),
            If(bag == bag1, 
                stones(bag2, next) == stones(bag2, current),
                stones(bag1, next) == stones(bag1, current))
        )
        return And(preconditions, effects)

    # Action conditions
    def apply_action(action, current, next):
        return Or(
            And(action == pickup, pickup_action(current, next)),
            And(action == put_in_bag1, put_in_bag_action(current, next, bag1)),
            And(action == put_in_bag2, put_in_bag_action(current, next, bag2))
        )

    # Initial state
    s.add(stones(hand, initial_state) == IntVal(0))
    s.add(stones(bag1, initial_state) == IntVal(0))
    s.add(stones(bag2, initial_state) == IntVal(0))
    s.add(stones(pile, initial_state) == IntVal(2))

    # Goal state
    s.add(And(
        stones(hand, goal_state) == IntVal(0),
        stones(bag1, goal_state) == IntVal(1),
        stones(bag2, goal_state) == IntVal(1),
        stones(pile, goal_state) == IntVal(0)
    ))

    # Actions
    for i in range(len(actions)):
        s.add(apply_action(actions[i], all_states[i], all_states[i+1]))

    return s, all_states, actions

solver, states, actions = bag_pile()

if solver.check() == sat:
    m = solver.model()
    for i, (state, action) in enumerate(zip(states, actions + [None])):
        print(f"State {i}:")
        print(f"  Hand: {m.evaluate(stones(hand, state))} stone(s)")
        print(f"  Bag1: {m.evaluate(stones(bag1, state))} stone(s)")
        print(f"  Bag2: {m.evaluate(stones(bag2, state))} stone(s)")
        print(f"  Pile: {m.evaluate(stones(pile, state))} stone(s)")
        if action is not None:
            print(f"Action: {m.evaluate(action)}")
    print("Goal reached!")
else:
    print("No solution found.")
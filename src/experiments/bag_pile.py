from z3 import *

# Define Hand states
Hand = Datatype('Hand')
Hand.declare('empty')
Hand.declare('occupied')
Hand = Hand.create()

Bag = Datatype('Bag')
Bag.declare('empty')
Bag.declare('holds_stones', ('stones', IntSort()))
Bag = Bag.create()

Pile = Datatype('Pile')
Pile.declare('empty')
Pile.declare('holds_stones', ('stones', IntSort()))
Pile = Pile.create()

# Declare objects
HandObj = Const('HandObj', Hand)
Bag1 = Const('Bag1', Bag)
Bag2 = Const('Bag2', Bag)
PileObj = Const('PileObj', Pile)

# Initial state
s.add(HandObj == Hand.empty)

# Object and state
Object = DeclareSort("Object")
State = DeclareSort("State")
Action = DeclareSort("Action")

# States and emptiness
stones = Function("Stones", Object, State, IntSort())

# Objects
hand = Const("hand", Object)
bag1 = Const("bag1", Object)
bag2 = Const("bag2", Object)
pile = Const("pile", Object)

# Max steps and solver instantiation
intermediate_steps = 10
s = Solver()

# Actions
pickup = Function("pickup", State, State, BoolSort())
put_in_bag1 = Const("put_in_bag1", Action)
put_in_bag2 = Const("put_in_bag2", Action)
all_actions = ["pickup", "put_in_bag1", "put_in_bag2"]

# States
initial_state = Const("initial_state", State)
goal_state = Const("goal_state", State)
intermediate_states = [
    Const(f"state_{i}", State) for i in range(1, intermediate_steps + 1)
]
actions = [
    EnumSort(f"Action_{i}", [*[action for action in all_actions]])
    for i in range(1, intermediate_steps + 1)
]
all_states = [initial_state] + intermediate_states + [goal_state]


def bag_pile():
    # Add bag capacity constraint for all states
    for state in all_states:
        s.add(stones(bag1, state) <= 1)
        s.add(stones(bag2, state) <= 1)

    # Empty and non-empty states
    def empty(obj, state):
        return stones(obj, state) == 0

    def not_empty(obj, state):
        return stones(obj, state) != 0

    def hand_transition(h_curr, h_next):
        return Xor(
            And(empty(hand, h_curr), stones(hand, h_next) + 1),
            And(stones(hand, h_curr), empty(hand, h_next)),
        )

    def bag_transition(b_curr, b_next):
        return Xor(
            And(empty(bag1, b_curr), stones(bag1, b_next) + 1),
            And(stones(bag1, b_curr), empty(bag1, b_next)),
        )

    def pickup(current, next):
        preconditions = And(
            stones(hand, current) == 0, stones(pile, current) > 0
        )
        effects = And(
            stones(pile, next) == stones(pile, current) - 1,
            stones(hand, next) == stones(hand, current) + 1,
            stones(bag1, next) == stones(bag1, current),
            stones(bag2, next) == stones(bag2, current),
        )
        return Implies(preconditions, effects)

    def put_in_bag_action(current, next, bag):
        preconditions = And(
            stones(hand, current) > 0,
            stones(bag, current) < 1,  # Ensure the bag has capacity
        )
        effects = And(
            stones(hand, next) == stones(hand, current) - 1,
            stones(bag, next) == stones(bag, current) + 1,
            stones(pile, next) == stones(pile, current),
            If(
                bag == bag1,
                stones(bag2, next) == stones(bag2, current),
                stones(bag1, next) == stones(bag1, current),
            ),
        )
        return Implies(preconditions, effects)

    # Action conditions

    def apply_action(action, current, next):
        return Or(
            pickup(current, next),
            put_in_bag_action(current, next, bag1),
            put_in_bag_action(current, next, bag2),
        )

    # Initial state
    s.add(stones(hand, initial_state) == 0)
    s.add(stones(bag1, initial_state) == 0)
    s.add(stones(bag2, initial_state) == 0)
    s.add(stones(pile, initial_state) == 2)

    # Goal state
    goal = Or([
        And(
            stones(hand, state) == 0,
            stones(bag1, state) == 1,
            stones(bag2, state) == 1,
            stones(pile, state) == 0,
        )
        for state in all_states
    ])
    s.add(goal)

    # Actions
    for i in range(len(actions)):
        # s.add(Or(*[action for action in all_actions]))
        s.add(apply_action(actions[i], all_states[i], all_states[i + 1]))

    return s, all_states, actions, goal


solver, states, actions, goal = bag_pile()

if solver.check() == sat:
    m = solver.model()
    # Use a different variable name instead of 'goal' for the loop, e.g., 'goal_state'
    for i, (state, action) in enumerate(zip(states, actions)):
        print(f"State {i}:")
        print(f"  Hand: {m.evaluate(stones(hand, state))} stone(s)")
        print(f"  Bag1: {m.evaluate(stones(bag1, state))} stone(s)")
        print(f"  Bag2: {m.evaluate(stones(bag2, state))} stone(s)")
        print(f"  Pile: {m.evaluate(stones(pile, state))} stone(s)")
        if action is not None:
            print(f"Action: {m.evaluate(action[i])}")
        # Use the original 'goal' variable here as intended
        if m.evaluate(goal) == True:
            print(f"Goal reached on step {i}")
            break
    # print("Goal reached!")
else:
    print("No solution found.")

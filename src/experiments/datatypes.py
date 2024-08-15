from z3 import *

# Define Hand states
Hand = Datatype("Hand")
Hand.declare("empty")
Hand.declare("occupied")
Hand = Hand.create()

Bag = Datatype("Bag")
Bag.declare("empty")
Bag.declare("full")
Bag = Bag.create()

Pile = Datatype("Pile")
Pile.declare("empty")
Pile.declare("stones", ("val", IntSort()))
Pile = Pile.create()

# Get all the keys from column 'name' if rows contain only zeroes in corresponding columns after 'index'

ActionType = Datatype("ActionType")
ActionType.declare("pickup")
ActionType.declare("put_bag", ("bag", Bag))
ActionType.declare("noop")
ActionType = ActionType.create()

x = 3
x = Int(3)
x = Const('x', IntSort())

# Declare objects
# h = Const("HandObj", Hand)
# b1 = Const("Bag1", Bag)
# b2 = Const("Bag2", Bag)
# p = Const("PileObj", Pile)

# Max steps and solver instantiation
intermediate_steps = 10
max_steps = intermediate_steps + 1
s = Solver()

# State for each time step
hand_states = [Const(f"hand_{i}", Hand) for i in range(max_steps)]
bag1_states = [Const(f"bag1_{i}", Bag) for i in range(max_steps)]
bag2_states = [Const(f"bag2_{i}", Bag) for i in range(max_steps)]
pile_states = [Const(f"pile_{i}", Pile) for i in range(max_steps)]
actions = [Const(f"action_{i}", ActionType) for i in range(max_steps)]

# Initial state
s.add(hand_states[0] == Hand.empty)
s.add(bag1_states[0] == Bag.empty)
s.add(bag2_states[0] == Bag.empty)
s.add(pile_states[0] == Pile.stones(2))
s.add(actions[0] == ActionType.noop)

prove(Pile.val(pile_states[0]) + 2 == 4)
initial, *state = zip(hand_states, bag1_states, bag2_states, pile_states, actions)

# Pickup action
def pickup(hand, pile):
    return And(hand == Hand.occupied, Pile.val(pile) == Pile.val(pile) - 1)

# Putting in bag action
def put_in_bag(hand, bag):
    return And(hand == Hand.empty, bag == Bag.full)

# State transitions
for step in range(max_steps - 1):
    hand, bag1, bag2, pile, action = state[step]
    next_hand, next_bag1, next_bag2, next_pile, next_action = state[step + 1]

    pickup_condition = And(
        hand == Hand.empty, pile != Pile.empty
    )
    # Pickup action
    s.add(Implies(pickup_condition, pickup(hand, pile)))

    # Put in bag action
    s.add(Implies(action == ActionType.put_in_bag(b1), put_in_bag(next_hand, bag1)))
    s.add(Implies(action == ActionType.put_in_bag(b2), put_in_bag(next_hand, bag2)))

    # No-op action

# print([i for i in state])
# if solver.check() == sat:
#     m = solver.model()
#     # Use a different variable name instead of 'goal' for the loop, e.g., 'goal_state'
#     for i, (state, action) in enumerate(zip(states, actions)):
#         print(f"State {i}:")
#         print(f"  Hand: {m.evaluate(stones(hand, state))} stone(s)")
#         print(f"  Bag1: {m.evaluate(stones(bag1, state))} stone(s)")
#         print(f"  Bag2: {m.evaluate(stones(bag2, state))} stone(s)")
#         print(f"  Pile: {m.evaluate(stones(pile, state))} stone(s)")
#         if action is not None:
#             print(f"Action: {m.evaluate(action[i])}")
#         # Use the original 'goal' variable here as intended
#         if m.evaluate(goal) == True:
#             print(f"Goal reached on step {i}")
#             break
#     # print("Goal reached!")
# else:
#     print("No solution found.")

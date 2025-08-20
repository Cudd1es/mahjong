from wall import *

wall = create_wall()
shuffle_wall(wall)

hands, remaining = deal_tiles(wall)

for i, hand in enumerate(hands):
    print(f"Player {i+1} hand ({len(hand)} tiles): {hand}")

print()
for i, hand in enumerate(hands):
    print(f"Player {i+1} hand ({len(hand)} tiles): {sort_hand(hand)}")
    print(set(hand) == set(sort_hand(hand)))


print(f"Remaining wall: {len(remaining)} tiles")

from wall import *

wall = create_wall()
shuffle_wall(wall)

hands, remaining = deal_tiles(wall)

for i, hand in enumerate(hands):
    print(f"Player {i+1} hand ({len(hand)} tiles): {hand}")

print()
for i, hand in enumerate(hands):
    formatted_sorted_hand = [f"({i}){tile}" for i, tile in enumerate(sort_hand(hand))]
    print(f"Player {i+1} hand ({len(hand)} tiles): {" ".join(formatted_sorted_hand)}")
    print (sort_hand(hand)[7])
    print(set(hand) == set(sort_hand(hand)))


print(f"Remaining wall: {len(remaining)} tiles")

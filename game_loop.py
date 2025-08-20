from wall import *
from player import *

def play_round(round_number):
    wall = create_wall()
    shuffle_wall(wall)

    players = [
        Player("P1", "E"),
        Player("P2", "S"),
        Player("P3", "W"),
        Player("P4", "N")
    ]

    hands, wall = deal_tiles(wall, 4)
    for i, p in enumerate(players):
        p.hand = hands[i]
        p.sort_hand()

    for p in players:
        print(f"{p.name} ({p.wind}) hand: {p.hand}")

    # simulate the first $round_number rounds

    for turn in range(round_number):
        current_player = players[turn%4]
        print(f"\n round {turn} {current_player.name} ({current_player.wind})'s turn---")

        if turn != 0:
            drawn_tile = current_player.draw(wall)
            print(f"{current_player.name} ({current_player.wind}) drew {drawn_tile}")

        current_player.sort_hand()
        print(f"Hand after draw: {current_player.hand}")

        discard_index = random.randint(0, len(current_player.hand)-1)
        print(f"Discard index {discard_index} out of {len(current_player.hand)-1}--")
        discarded = current_player.discard(discard_index)
        print(f"{current_player.name} discarded {discarded}")

        print(f"{current_player.name} ({current_player.wind})'s hand: {current_player.hand}")


play_round(4)
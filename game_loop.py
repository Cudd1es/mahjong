from wall import *
from player import *
import random

def play_round(round_number = -1):
    wall = create_wall()
    shuffle_wall(wall)

    # set human player as P1 and rest player are AI
    players = [
        HumanPlayer("P1", "E"),
        AIPlayer("P2", "S"),
        AIPlayer("P3", "W"),
        AIPlayer("P4", "N")
    ]

    hands, wall = deal_tiles(wall, 4)
    for i, p in enumerate(players):
        p.hand = hands[i]
        p.sort_hand()

    # separate dead wall (14 tiles)
    dead_wall = wall[14:]
    live_wall = wall[:-14]

    for p in players:
        print(f"{p.name} ({p.wind}) hand: {p.hand}")

    # simulate the first $round_number rounds, if round_number is -1 it will loop until the game ends in draw
    if round_number == -1:
        turn = 0
        while len(live_wall) > 0:
            current_player = players[turn%4]
            print(f"\nround {turn} {current_player.name} ({current_player.wind})'s turn---")

            if turn != 0:
                drawn_tile = current_player.draw(live_wall)
                if drawn_tile is None:
                    print("No more tiles to draw, game ends in draw")
                    break
                print(f"{current_player.name} ({current_player.wind}) drew {drawn_tile}")

            current_player.sort_hand()
            print(f"Hand: {current_player.hand}")

            discard_index = current_player.decide_discard()
            #print(f"Discard index {discard_index} out of {len(current_player.hand) - 1}--")
            discarded = current_player.discard(discard_index)
            print(f"{current_player.name} discarded {discarded}")

            if len(live_wall) == 0:
                print("\nNo more tiles in live wall. The game ends in draw")
                break
            turn += 1
        return

    for turn in range(round_number):
        current_player = players[turn%4]
        print(f"\nround {turn} {current_player.name} ({current_player.wind})'s turn---")

        if turn != 0:
            drawn_tile = current_player.draw(wall)
            print(f"{current_player.name} ({current_player.wind}) drew {drawn_tile}")

        current_player.sort_hand()
        print(f"Hand after draw: {current_player.hand}")

        discard_index = current_player.decide_discard()
        #print(f"Discard index {discard_index} out of {len(current_player.hand)-1}--")
        discarded = current_player.discard(discard_index)
        print(f"{current_player.name} discarded {discarded}")

        print(f"{current_player.name} ({current_player.wind})'s hand: {current_player.hand}")

        # print discarded zone
        print(f"\ndiscard zone-----")
        for p in players:
            print(f"{p.name} ({p.wind}): {p.discards}")

if __name__ == "__main__":
    play_round()


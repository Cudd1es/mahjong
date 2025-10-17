# CLI Riichi Mahjong Game 

A full-featured, modular, and extensible implementation of **Japanese Riichi Mahjong** in Python.  
This project aims to provide a playable console game, rich yaku detection, AI and human player support, and code structure suitable for extension or integration into other systems.

---

## Features

- **Complete Riichi rules** (14-tile hands, 4-player, wall, dead wall, draws, and discards)
- **Rich yaku detection**: standard, yakuman, and many advanced yaku (including riichi, iipeikou, ryanpeikou, sanshoku doujun, sanshoku doukou, chiitoitsu, kokushi musou, etc.)
- **Human and AI player support** (AI discards randomly, always declares riichi/tsumo if available)
- **Supports melds (pon, chi, kan), red fives (aka dora), and proper hand normalization**
- **Riichi logic**: restricts discards after declaring riichi; tracks riichi declaration and discards for ipatsu/yaku
- **Tenpai (waiting hand) calculation and recommended discards**
- **Role separation**: clear modules for wall, tiles, player, hand checker, melds, and yaku calculation
- **Easily extensible**: plug in better AI, yaku, scoring, multiplayer, or GUI

---

## Requirements

- Python 3.9+ 

---

## Project Structure

```
mahjong/
  ├── game_loop.py         # Main game logic and turn loop
  ├── player.py            # Player, AIPlayer, HumanPlayer classes and discard logic
  ├── tiles.py             # Tile class and tile operations
  ├── wall.py              # Wall creation, shuffling, tile dealing, sorting
  ├── hand_checker.py      # Hand evaluation: winning hand, tenpai, discard recommendations
  ├── melds.py             # Chi, pon, kan detection and meld handling
  ├── yaku.py              # Yaku detection (all major Riichi yaku supported)
```

---

## Usage

```bash
python game_loop.py
```
---

## Key Rules & Features

- **Red fives (Aka Dora)** are supported; red five and normal five are treated equivalently in hand operations and yaku calculation.
- **Meld calls**: AI and humans can chi, pon, kan according to standard Riichi rules; riichi disables chi/pon/kan.
- **Riichi**: When a closed player is in tenpai, they can declare riichi, after which only drawn tiles can be discarded.
- **Yaku calculation** includes common hands and many advanced patterns:  
  iipeikou, ryanpeikou, sanshoku doujun, sanshoku doukou, chiitoitsu, kokushi musou, tanyao, yakuhai, pinfu, toitoi, honitsu, chinitsu, etc.
- **Tenpai detection and discard suggestion**: On each turn, the game can recommend all discards that would result in a waiting hand and what tiles would complete your hand.

---

## Example: Tenpai and Riichi Flow

```
P1 (E) drew 5m
Melds: []
Hand: 2m 3m 4m 6p 7p 8p 1s 2s 3s 4s 0s 8s 9s
you can discard the following to Tenpai:
4s: waiting: (5s, 8s)
8s: waiting: (4s, 5s)
riichi available! Do you want to riichi? ([Y]/n):
choose a tile index to discard:
```

---



## License

MIT License

---


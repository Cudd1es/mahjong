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
- **StepGameEngine**: New state-machine based engine architecture for easier integration with UIs, web servers, and AI training.
- **Furiten Check**: Implemented realistic Furiten (Sacred Discard) rules to prevent invalid Ron calls.
- **Easily extensible**: plug in better AI, yaku, scoring, multiplayer, or GUI

---


## Project Structure

```
mahjong/
mahjong/
  ├── play_step_cli.py     # Interactive CLI game using the new StepGameEngine
  ├── run_step_simulation.py # Automated simulation script for validation
  ├── src/
  │   ├── step_game_engine.py  # New state-machine game engine
  │   ├── game_engine.py       # Legacy game engine
  │   ├── models/              # Player, Tile, Wall models
  │   ├── core/                # Core logic (Yaku, Hand Checker, Scoring, Melds)
```

---
## Requirements

- Python 3.9+ 

---

## Usage

## Usage
  
### Interactive Play
New Step-Based Engine (Recommended):
```bash
python play_step_cli.py
```

Legacy Engine:
```bash
python run_cli.py
```

### Web Interface
This project now includes a modern, high-fidelity Web UI built with **React, TailwindCSS, and FastAPI**.
- **Visuals**: Features a 3D Gold/Wood Compass, Crystal Orb action buttons (Ron, Pon, Tsumo), and high-quality ivory tile textures.
- **Glassmorphism**: Clean, modern UI overlays.
- **Interactive**: Real-time gameplay with visual feedback for discards, melds, and winning.

### Simulation / Verification
Run automated games to verify engine logic and AI performance:
```bash
python run_step_simulation.py 20
```

---

## Project Structure

```
mahjong/
├── play_step_cli.py       # Interactive CLI game
├── run_step_simulation.py # Automated simulation script
├── server/                # FastAPI Backend
│   ├── main.py            # API Entry point
│   └── schemas.py         # Pydantic models
├── web/                   # React Frontend
│   ├── src/               # React components (Table, Tile, Hand)
│   └── public/            # Game assets (Compass, Crystals, Tiles)
├── src/
│   ├── step_game_engine.py  # New state-machine game engine
│   ├── models/              # Player, Tile, Wall models
│   └── core/                # Core logic (Yaku, Hand Checker, Scoring, Melds)
```

---

## Requirements

- Python 3.9+ 
- Node.js (for Web UI)
- Pillow (for asset processing)

---

## Usage
  
### Interactive Play (CLI)
New Step-Based Engine (Recommended):
```bash
python play_step_cli.py
```

### Web Interface
1. Start the Backend:
```bash
uvicorn server.main:app --reload
```
2. Start the Frontend:
```bash
cd web
npm run dev
```

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


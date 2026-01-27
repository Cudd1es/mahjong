
import React, { useState, useEffect } from 'react';
import Hand from './Hand';
import Tile from './Tile';

const API_BASE = "http://localhost:8000";

const Table = () => {
    const [gameState, setGameState] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchState = async () => {
        try {
            const res = await fetch(`${API_BASE}/state`);
            const data = await res.json();
            setGameState(data);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const startGame = async () => {
        try {
            setLoading(true);
            await fetch(`${API_BASE}/start`, { method: 'POST' });
            await fetchState();
        } catch (err) {
            setError("Failed to start game");
        }
    };

    // Polling for MVP (WebSocket is better but harder)
    useEffect(() => {
        fetchState();
        const interval = setInterval(fetchState, 1000);
        return () => clearInterval(interval);
    }, []);

    const handleDiscard = async (index) => {
        // Optimistic UI update? No, wait for refresh.
        // Identify self (MVP: Assume Player 0 is Human/User for now)
        // Check if it's my turn
        if (!gameState) return;
        const myIdx = 0; // Fixed for now
        if (gameState.current_player_idx !== myIdx) return;

        try {
            await fetch(`${API_BASE}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: 'discard',
                    player_idx: myIdx,
                    tile_index: index
                })
            });
            fetchState();
        } catch (err) {
            console.error(err);
        }
    };

    if (loading && !gameState) return <div className="text-white">Loading...</div>;
    if (error) return <div className="text-red-500">Error: {error}</div>;

    // Check if game is not really started (IDLE or empty players)
    if (!gameState || !gameState.players || gameState.players.length === 0) {
        return (
            <div className="flex w-full h-screen items-center justify-center bg-gray-900">
                <button
                    onClick={startGame}
                    className="bg-blue-600 text-white px-8 py-4 rounded-xl text-2xl font-bold hover:bg-blue-500 transition-colors shadow-lg"
                >
                    Start Game
                </button>
            </div>
        );
    }

    // Layout
    const me = gameState.players[0];
    const right = gameState.players[1];
    const top = gameState.players[2];
    const left = gameState.players[3];

    // Helper to render river
    const renderRiver = (player, playerIdx) => {
        const isDiscarder = gameState.last_discard_player_idx === playerIdx;
        return (
            <div className="flex flex-wrap w-64 md:w-80 gap-1 content-start justify-center p-2">
                {player.discards.map((t, i) => {
                    const isLast = isDiscarder && i === player.discards.length - 1;
                    return (
                        <div key={i} className={`relative transition-all duration-300 ${isLast ? 'scale-110 z-10' : 'scale-75'}`}>
                            <Tile tile={t} />
                            {isLast && (
                                <div className="absolute inset-0 border-4 border-yellow-400 rounded animate-pulse shadow-[0_0_15px_rgba(255,215,0,0.8)] pointer-events-none"></div>
                            )}
                            {isLast && (
                                <div className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-yellow-300 font-bold text-xs bg-black bg-opacity-70 px-1 rounded">
                                    Current
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        );
    };

    const renderMelds = (player) => {
        if (!player.melds || player.melds.length === 0) return null;
        return (
            <div className="flex gap-2">
                {player.melds.map((meld, i) => (
                    <div key={i} className="flex gap-0.5 p-1 rounded">
                        {meld.map((t, j) => (
                            <div key={j} className="scale-75">
                                <Tile tile={t} />
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        );
    };

    // Helper for buttons
    const handleAction = async (type) => {
        try {
            await fetch(`${API_BASE}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: type,
                    player_idx: 0 // Me
                })
            });
            fetchState();
        } catch (err) { console.error(err); }
    };

    return (
        <div className="relative w-full h-screen flex flex-col justify-between overflow-hidden bg-cover bg-center" style={{ backgroundImage: "url('/table_felt.png')" }}>
            {/* Top Player (Opponent) */}
            <div className="absolute top-16 w-full flex flex-col items-center rotate-180 opacity-90 z-0">
                {renderRiver(top, 2)}
                <div className="flex gap-4 items-center mt-2">
                    <div className="flex gap-1 p-2 rounded">
                        {top.hand.map((_, i) => <div key={i} className="w-8 h-12 bg-cover bg-center border border-white rounded" style={{ backgroundImage: "url('/tile_back.png')" }}></div>)}
                    </div>
                    {renderMelds(top)}
                </div>
            </div>

            {/* Left Player */}
            <div className="absolute left-24 top-1/2 -translate-y-1/2 flex flex-col items-center rotate-90 opacity-90 origin-center z-0">
                {renderRiver(left, 3)}
                <div className="flex gap-4 items-center mt-2">
                    <div className="flex gap-1 p-2 rounded">
                        {left.hand.map((_, i) => <div key={i} className="w-8 h-12 bg-cover bg-center border border-white rounded" style={{ backgroundImage: "url('/tile_back.png')" }}></div>)}
                    </div>
                    {renderMelds(left)}
                </div>
            </div>

            {/* Right Player */}
            <div className="absolute right-24 top-1/2 -translate-y-1/2 flex flex-col items-center -rotate-90 opacity-90 origin-center z-0">
                {renderRiver(right, 1)}
                <div className="flex gap-4 items-center mt-2">
                    <div className="flex gap-1 p-2 rounded">
                        {right.hand.map((_, i) => <div key={i} className="w-8 h-12 bg-cover bg-center border border-white rounded" style={{ backgroundImage: "url('/tile_back.png')" }}></div>)}
                    </div>
                    {renderMelds(right)}
                </div>
            </div>

            {/* Center Area (Info) - Compass Style */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-contain bg-center bg-no-repeat flex flex-col items-center justify-center text-white z-10" style={{ backgroundImage: "url('/compass_dial.png')" }}>
                <div className="text-3xl font-black text-yellow-100 drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] mt-[-10px]">
                    {['E', 'S', 'W', 'N'][gameState.current_player_idx]}
                </div>
                <div className="text-xs font-bold text-yellow-200 mt-1 drop-shadow-md">Round {gameState.round_count}</div>
                <div className="text-[10px] text-gray-300 drop-shadow-md">Wall: {gameState.live_wall_count}</div>

                {gameState.phase === 'WAIT_DISCARD' && gameState.current_player_idx === 0 && (
                    <div className="absolute -bottom-16 w-full text-center text-yellow-300 animate-bounce font-bold text-xl drop-shadow-lg">YOUR TURN</div>
                )}
            </div>

            {/* Action Buttons - Crystal Orbs */}
            {((gameState.phase === 'WAIT_RESPONSE' && gameState.valid_actions && gameState.valid_actions.length > 0) || gameState.can_tsumo) && (
                <div className="absolute bottom-32 right-12 flex flex-col gap-4 z-50 animate-bounce-subtle items-center">
                    {gameState.can_tsumo && (
                        <button onClick={() => handleAction('tsumo')} className="hover:scale-110 transition-transform">
                            <img src="/btn_tsumo.png" alt="Tsumo" className="w-28 h-28 drop-shadow-2xl animate-winner" />
                        </button>
                    )}
                    {gameState.valid_actions && gameState.valid_actions.includes('ron') && (
                        <button onClick={() => handleAction('ron')} className="hover:scale-110 transition-transform">
                            <img src="/btn_ron.png" alt="Ron" className="w-20 h-20 drop-shadow-xl animate-pulse" />
                        </button>
                    )}
                    {gameState.valid_actions && gameState.valid_actions.includes('kan') && (
                        <button onClick={() => handleAction('kan')} className="hover:scale-110 transition-transform">
                            <img src="/btn_kan.png" alt="Kan" className="w-20 h-20 drop-shadow-lg" />
                        </button>
                    )}
                    {gameState.valid_actions && gameState.valid_actions.includes('pon') && (
                        <button onClick={() => handleAction('pon')} className="hover:scale-110 transition-transform">
                            <img src="/btn_pon.png" alt="Pon" className="w-20 h-20 drop-shadow-lg" />
                        </button>
                    )}
                    {gameState.valid_actions && gameState.valid_actions.includes('chi') && (
                        <button onClick={() => handleAction('chi')} className="hover:scale-110 transition-transform">
                            <img src="/btn_chi.png" alt="Chi" className="w-20 h-20 drop-shadow-lg" />
                        </button>
                    )}
                    {!gameState.can_tsumo && (
                        <button onClick={() => handleAction('skip')} className="hover:scale-110 transition-transform">
                            <img src="/btn_skip.png" alt="Skip" className="w-16 h-16 drop-shadow-md opacity-80 hover:opacity-100" />
                        </button>
                    )}
                </div>
            )}


            {/* Bottom Player (Me) */}
            <div className="absolute bottom-4 w-full flex flex-col items-center z-10">
                {/* My Discards - Closer to center (Top of hand area) */}
                <div className="mb-8">
                    {renderRiver(me, 0)}
                </div>

                <div className="relative flex justify-center items-end gap-8 w-full max-w-5xl">
                    <Hand
                        tiles={me.hand}
                        isTurn={gameState.current_player_idx === 0 && gameState.phase === 'WAIT_DISCARD'}
                        canDiscard={gameState.current_player_idx === 0 && gameState.phase === 'WAIT_DISCARD'}
                        onDiscard={handleDiscard}
                    />
                    {renderMelds(me)}
                </div>
                <div className="mt-2 px-6 py-2 bg-contain bg-center bg-no-repeat text-white font-bold text-shadow-md flex items-center justify-center w-56 h-10 text-sm" style={{ backgroundImage: "url('/score_plate.png')" }}>
                    {me.name} ({me.wind}) · {me.score}
                </div>
            </div>
        </div >
    );
};

export default Table;

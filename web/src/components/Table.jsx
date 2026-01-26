
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
            <div className="flex flex-wrap w-64 md:w-80 gap-1 content-start justify-center bg-black bg-opacity-10 p-2 rounded-lg">
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
                    <div key={i} className="flex gap-0.5 bg-black bg-opacity-20 p-1 rounded">
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
        <div className="relative w-full h-screen bg-green-800 flex flex-col justify-between overflow-hidden">
            {/* Top Player (Opponent) */}
            <div className="absolute top-16 w-full flex flex-col items-center rotate-180 opacity-90 z-0">
                {renderRiver(top, 2)}
                <div className="flex gap-4 items-center mt-2">
                    <div className="flex gap-1 bg-black bg-opacity-30 p-2 rounded">
                        {top.hand.map((_, i) => <div key={i} className="w-8 h-12 bg-blue-900 border border-white rounded"></div>)}
                    </div>
                    {renderMelds(top)}
                </div>
            </div>

            {/* Left Player */}
            <div className="absolute left-24 top-1/2 -translate-y-1/2 flex flex-col items-center rotate-90 opacity-90 origin-center z-0">
                {renderRiver(left, 3)}
                <div className="flex gap-4 items-center mt-2">
                    <div className="flex gap-1 bg-black bg-opacity-30 p-2 rounded">
                        {left.hand.map((_, i) => <div key={i} className="w-8 h-12 bg-blue-900 border border-white rounded"></div>)}
                    </div>
                    {renderMelds(left)}
                </div>
            </div>

            {/* Right Player */}
            <div className="absolute right-24 top-1/2 -translate-y-1/2 flex flex-col items-center -rotate-90 opacity-90 origin-center z-0">
                {renderRiver(right, 1)}
                <div className="flex gap-4 items-center mt-2">
                    <div className="flex gap-1 bg-black bg-opacity-30 p-2 rounded">
                        {right.hand.map((_, i) => <div key={i} className="w-8 h-12 bg-blue-900 border border-white rounded"></div>)}
                    </div>
                    {renderMelds(right)}
                </div>
            </div>

            {/* Center Area (Info) */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-40 bg-green-900 bg-opacity-80 rounded-xl shadow-2xl border-2 border-yellow-600 flex flex-col items-center justify-center text-white z-10">
                <div className="text-xl font-bold text-yellow-400">Round {gameState.round_count}</div>
                <div className="text-lg">Turn: {gameState.players[gameState.current_player_idx].name}</div>
                <div className="text-sm text-gray-300">Wall: {gameState.live_wall_count}</div>
                <div className="mt-1 px-2 py-0.5 bg-black rounded text-xs">{gameState.phase}</div>

                {gameState.phase === 'WAIT_DISCARD' && gameState.current_player_idx === 0 && (
                    <div className="mt-2 text-yellow-300 animate-bounce font-bold">YOUR TURN</div>
                )}
            </div>

            {/* Action Buttons - Visible but Non-Blocking - Moved to Right Side */}
            {gameState.phase === 'WAIT_RESPONSE' && gameState.valid_actions && gameState.valid_actions.length > 0 && (
                <div className="absolute bottom-32 right-12 flex flex-col gap-3 z-50 animate-bounce-subtle">
                    {gameState.valid_actions.includes('ron') && (
                        <button onClick={() => handleAction('ron')} className="bg-red-600 text-white w-20 h-20 rounded-full shadow-lg text-2xl font-black border-4 border-white animate-pulse hover:scale-110 transition-transform">RON</button>
                    )}
                    {gameState.valid_actions.includes('kan') && (
                        <button onClick={() => handleAction('kan')} className="bg-purple-600 text-white w-16 h-16 rounded-full shadow-lg text-xl font-bold border-2 border-white hover:scale-110 transition-transform">Kan</button>
                    )}
                    {gameState.valid_actions.includes('pon') && (
                        <button onClick={() => handleAction('pon')} className="bg-blue-600 text-white w-16 h-16 rounded-full shadow-lg text-xl font-bold border-2 border-white hover:scale-110 transition-transform">Pon</button>
                    )}
                    {gameState.valid_actions.includes('chi') && (
                        <button onClick={() => handleAction('chi')} className="bg-green-600 text-white w-16 h-16 rounded-full shadow-lg text-xl font-bold border-2 border-white hover:scale-110 transition-transform">Chi</button>
                    )}
                    <button onClick={() => handleAction('skip')} className="bg-gray-500 text-white w-14 h-14 rounded-full shadow-lg text-md font-bold border-2 border-gray-300 hover:scale-110 transition-transform">Skip</button>
                </div>
            )}



            {/* Bottom Player (Me) */}
            <div className="absolute bottom-4 w-full flex flex-col items-center z-10">
                {/* My Discards - Closer to center (Top of hand area) */}
                <div className="mb-8">
                    {renderRiver(me, 0)}
                </div>

                <div className="relative flex justify-center items-end gap-8 bg-black bg-opacity-20 p-4 rounded-t-xl w-full max-w-5xl">
                    <Hand
                        tiles={me.hand}
                        isTurn={gameState.current_player_idx === 0 && gameState.phase === 'WAIT_DISCARD'}
                        canDiscard={gameState.current_player_idx === 0 && gameState.phase === 'WAIT_DISCARD'}
                        onDiscard={handleDiscard}
                    />
                    {renderMelds(me)}
                </div>
                <div className="text-white mt-2 font-bold bg-black bg-opacity-50 px-4 py-1 rounded-full">
                    {me.name} ({me.wind}) · Score: {me.score}
                </div>
            </div>
        </div >
    );
};

export default Table;

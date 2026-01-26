
import React from 'react';
import Tile from './Tile';

const Hand = ({ tiles, onDiscard, isTurn, canDiscard }) => {
    return (
        <div className="flex gap-1 md:gap-2 items-end h-20 md:h-24 px-4 bg-opacity-20 bg-black rounded-lg">
            {tiles.map((t, idx) => (
                <Tile
                    key={`${t}-${idx}`}
                    tile={t}
                    onClick={() => canDiscard && onDiscard && onDiscard(idx)}
                    selected={false} // layout logic could go here
                />
            ))}
        </div>
    );
};

export default Hand;

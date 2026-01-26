
import React from 'react';
import { getTileUnicode, isRedFive } from '../utils/tileMapping';

const Tile = ({ tile, onClick, selected, isDora }) => {
    const unicode = getTileUnicode(tile);
    const isRed = isRedFive(tile);

    // Determine color
    // Standard Unicode tiles are black/white glyphs.
    // We can use text-color to tint them? 
    // Usually only needed for Red 5.

    return (
        <div
            onClick={() => onClick && onClick(tile)}
            className={`
                relative
                flex items-center justify-center
                w-10 h-14 md:w-12 md:h-16
                bg-white border border-gray-300 rounded-md
                shadow-md select-none cursor-pointer
                transition-transform hover:-translate-y-1
                ${selected ? 'ring-2 ring-blue-500 -translate-y-2' : ''}
            `}
        >
            <span className={`text-4xl md:text-5xl leading-none ${isRed ? 'text-red-600' : 'text-black'}`}>
                {unicode}
            </span>

            {/* Helper text for debugging/clarity? Optional */}
            {/* <span className="absolute bottom-0 text-[8px] text-gray-400">{tile}</span> */}
        </div>
    );
};

export default Tile;

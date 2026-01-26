
export const getTileUnicode = (tileStr) => {
    // Standardize input (e.g. "1m" -> 1m, "5p" -> 5p)
    if (!tileStr) return "🀫"; // Back of tile

    // Handle Red 5 (0m, 0p, 0s) -> Treat as 5 for visual but maybe special color?
    // Unicode doesn't have red 5s distinctively. We usually color them red in CSS.
    let value = tileStr[0];
    let suit = tileStr[1];

    // Convert red 5 "0" to "5" for mapping
    if (value === '0') value = '5';

    const baseMap = {
        'm': 0x1F007, // 1m is 1F007 (🀇)
        's': 0x1F010, // 1s is 1F010 (🀐)
        'p': 0x1F019, // 1p is 1F019 (🀙)
        'z': 0x1F000  // East is 1F000 (🀀)
    };

    if (suit === 'z') {
        const honorMap = {
            'E': 0x1F000, // East
            'S': 0x1F001, // South
            'W': 0x1F002, // West
            'N': 0x1F003, // North
            'P': 0x1F004, // White (Haku) - Wait, Unicode order: E, S, W, N, Red, Green, White?
            // Actually:
            // 1F000: East
            // 1F001: South
            // 1F002: West
            // 1F003: North
            // 1F004: Red Dragon (Chun)
            // 1F005: Green Dragon (Hatsu)
            // 1F006: White Dragon (Haku)
            // My P, F, C mapping in backend: P=White(Haku/Blank), F=Green(Hatsu), C=Red(Chun)

            'C': 0x1F004, // Chun (Red)
            'F': 0x1F005, // Hatsu (Green)
            'P': 0x1F006  // Haku (White)
        };
        return String.fromCodePoint(honorMap[value] || 0x1F02B);
    }

    if (baseMap[suit]) {
        // value is 1-9
        let offset = parseInt(value) - 1;
        return String.fromCodePoint(baseMap[suit] + offset);
    }

    return tileStr; // Fallback
};

export const isRedFive = (tileStr) => {
    return tileStr && tileStr.startsWith('0');
};

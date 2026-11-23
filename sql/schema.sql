CREATE TABLE trial_sessions (
    session_id TEXT PRIMARY KEY,
    day TEXT NOT NULL,
    case_id TEXT NOT NULL,
    retailer TEXT NOT NULL,
    locale TEXT NOT NULL,
    device TEXT NOT NULL CHECK (device IN ('Mobile', 'Desktop')),
    variant TEXT NOT NULL CHECK (variant IN ('control', 'treatment')),
    engaged INTEGER NOT NULL CHECK (engaged IN (0, 1)),
    carts INTEGER NOT NULL CHECK (carts IN (0, 1)),
    purchases INTEGER NOT NULL CHECK (purchases IN (0, 1) AND purchases <= carts)
);

-- Create vendors table
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Create topics table
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Create command_mappings table
CREATE TABLE IF NOT EXISTS command_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_vendor_id INTEGER,
    target_vendor_id INTEGER,
    source_command TEXT NOT NULL,
    target_command TEXT NOT NULL,
    topic_id INTEGER,
    description TEXT,
    FOREIGN KEY (source_vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (target_vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Create command_categories table
CREATE TABLE IF NOT EXISTS command_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    topic_id INTEGER,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
); 
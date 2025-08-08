-- Step 1: Create the new table with ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `accounts_new` (
    `address`    VARCHAR(255) NOT NULL UNIQUE,
    `name`       VARCHAR(255),
    `crypto_type` INTEGER DEFAULT NULL,
    `balance`    TEXT DEFAULT NULL,
    `path`       VARCHAR(255) DEFAULT NULL,
    `root`       VARCHAR(255) DEFAULT NULL,
    `file_import` INTEGER DEFAULT 0,
    `category_id` VARCHAR(36) DEFAULT NULL,
    `total_transfers_count` INTEGER NOT NULL DEFAULT 0,
    `last_transfer_timestamp` TIMESTAMP,
    `oldest_transfer_timestamp` TIMESTAMP,
    FOREIGN KEY(`root`) REFERENCES `accounts`(`address`) ON DELETE CASCADE,
    FOREIGN KEY(`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE,
    PRIMARY KEY(`address`)
);

-- Step 2: Copy data from the old table
INSERT INTO accounts_new (
    address, name, crypto_type, balance, path, root, file_import,
    category_id, total_transfers_count, last_transfer_timestamp, oldest_transfer_timestamp
)
SELECT
    address, name, crypto_type, balance, path, root, file_import,
    category_id, total_transfers_count, last_transfer_timestamp, oldest_transfer_timestamp
FROM accounts;

-- Step 3: Drop the old table
DROP TABLE accounts;

-- Step 4: Rename the new table
ALTER TABLE accounts_new RENAME TO accounts;

-------------------------------------------------------

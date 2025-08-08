-- Step 1: Rename the old table
ALTER TABLE accounts RENAME TO accounts_old;

-- Step 2: Create the new table with ON DELETE CASCADE
CREATE TABLE `accounts` (
    `address`    VARCHAR(255) NOT NULL UNIQUE,
    `name`       VARCHAR(255),
    `crypto_type` INTEGER DEFAULT NULL,
    `balance`    INTEGER DEFAULT NULL,
    `path`       VARCHAR(255) DEFAULT NULL,
    `root`       VARCHAR(255) DEFAULT NULL,
    `file_import` INTEGER DEFAULT 0,
    `category_id` VARCHAR(36) DEFAULT NULL,
    FOREIGN KEY(`root`) REFERENCES `accounts`(`address`) ON DELETE CASCADE,
    FOREIGN KEY(`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE,
    PRIMARY KEY(`address`)
);

-- Step 3: Copy data from the old table
INSERT INTO accounts (
    address, name, crypto_type, balance, path, root, file_import,
    category_id
)
SELECT
    address, name, crypto_type, balance, path, root, file_import,
    category_id
FROM accounts_old;

-- Step 4: Drop the old table
DROP TABLE accounts_old;

---------------------------------------

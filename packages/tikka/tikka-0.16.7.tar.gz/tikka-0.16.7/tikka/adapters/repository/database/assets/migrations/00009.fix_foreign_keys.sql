---------------------------------------

-- Step 1: Rename the old table
ALTER TABLE categories RENAME TO categories_old;

-- Step 2: Create the new table with ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `categories` (
    `id`        VARCHAR(36) NOT NULL UNIQUE,
    `name`      VARCHAR(255),
    `expanded`  INTEGER DEFAULT 1,
    `parent_id` VARCHAR(36) DEFAULT NULL,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`parent_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO categories (id, name, expanded, parent_id)
SELECT id, name, expanded, parent_id FROM categories_old;

-- Step 4: Drop the old table
DROP TABLE categories_old;

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
    `total_transfers_count` INTEGER NOT NULL DEFAULT 0,
    `last_transfer_timestamp` TIMESTAMP,
    `oldest_transfer_timestamp` TIMESTAMP,
    FOREIGN KEY(`root`) REFERENCES `accounts`(`address`) ON DELETE CASCADE,
    FOREIGN KEY(`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE,
    PRIMARY KEY(`address`)
);

-- Step 3: Copy data from the old table
INSERT INTO accounts (
    address, name, crypto_type, balance, path, root, file_import,
    category_id, total_transfers_count, last_transfer_timestamp, oldest_transfer_timestamp
)
SELECT
    address, name, crypto_type, balance, path, root, file_import,
    category_id, total_transfers_count, last_transfer_timestamp, oldest_transfer_timestamp
FROM accounts_old;

-- Step 4: Drop the old table
DROP TABLE accounts_old;

-------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE identities RENAME TO identities_old;

-- Step 2: Create the new table with ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `identities` (
    `index_`                INTEGER NOT NULL UNIQUE,
    `removable_on`          INTEGER,
    `next_creatable_on`     INTEGER,
    `status`                INTEGER NOT NULL,
    `address`               VARCHAR(255) NOT NULL,
    `old_address`           VARCHAR(255),
    `first_eligible_ud`     INTEGER NOT NULL DEFAULT 0,
    `name`                  VARCHAR(255),
    PRIMARY KEY(`index_`),
    FOREIGN KEY(`address`) REFERENCES `accounts`(`address`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO identities (index_, removable_on, next_creatable_on, status, address, old_address, first_eligible_ud, name)
SELECT index_, removable_on, next_creatable_on, status, address, old_address, first_eligible_ud, name FROM identities_old;

-- Step 4: Drop the old table
DROP TABLE identities_old;

-------------------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE smiths RENAME TO smiths_old;

-- Step 2: Create the new table with the foreign key and ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `smiths` (
    `identity_index`           INTEGER NOT NULL UNIQUE,
    `status`                   INTEGER NOT NULL,
    `expire_on`                TIMESTAMP,
    `certifications_received`  VARCHAR(255) NOT NULL DEFAULT '[]',
    `certifications_issued`    VARCHAR(255) NOT NULL DEFAULT '[]',
    PRIMARY KEY(`identity_index`),
    FOREIGN KEY(`identity_index`) REFERENCES `identities`(`index_`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO smiths (identity_index, status, expire_on, certifications_received, certifications_issued)
SELECT identity_index, status, expire_on, certifications_received, certifications_issued FROM smiths_old;

-- Step 4: Drop the old table
DROP TABLE smiths_old;

-----------------------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE authorities RENAME TO authorities_old;

-- Step 2: Create the new table with the foreign key and ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `authorities` (
    `identity_index`  INTEGER NOT NULL UNIQUE,
    `status`          INTEGER NOT NULL,
    PRIMARY KEY(`identity_index`),
    FOREIGN KEY(`identity_index`) REFERENCES `smiths`(`identity_index`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO authorities (identity_index, status)
SELECT identity_index, status FROM authorities_old;

-- Step 4: Drop the old table
DROP TABLE authorities_old;

---------------------------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE wallets RENAME TO wallets_old;

-- Step 2: Create the new table with the foreign key and ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `wallets` (
    `address`                 VARCHAR(255) NOT NULL UNIQUE,
    `crypto_type`             INTEGER,
    `encrypted_private_key`   VARCHAR(65535),
    `encryption_nonce`        VARCHAR(255),
    `encryption_mac_tag`      VARCHAR(255),
    PRIMARY KEY(`address`),
    FOREIGN KEY(`address`) REFERENCES `accounts`(`address`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO wallets (address, crypto_type, encrypted_private_key, encryption_nonce, encryption_mac_tag)
SELECT address, crypto_type, encrypted_private_key, encryption_nonce, encryption_mac_tag FROM wallets_old;

-- Step 4: Drop the old table
DROP TABLE wallets_old;

----------------------------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE passwords RENAME TO passwords_old;

-- Step 2: Create the new table with the foreign key and ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `passwords` (
    `root`                  VARCHAR(255) NOT NULL UNIQUE,
    `encrypted_password`    VARCHAR(255),
    `encryption_nonce`      VARCHAR(255),
    `encryption_mac_tag`    VARCHAR(255),
    PRIMARY KEY(`root`),
    FOREIGN KEY(`root`) REFERENCES `accounts`(`address`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO passwords (root, encrypted_password, encryption_nonce, encryption_mac_tag)
SELECT root, encrypted_password, encryption_nonce, encryption_mac_tag FROM passwords_old;

-- Step 4: Drop the old table
DROP TABLE passwords_old;

--------------------------------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE accounts_transfers RENAME TO accounts_transfers_old;

-- Step 2: Create the new table with the foreign key and ON DELETE CASCADE
CREATE TABLE IF NOT EXISTS `accounts_transfers` (
    `account_id`   VARCHAR(255) NOT NULL,
    `transfer_id`  VARCHAR(255) NOT NULL,
    PRIMARY KEY(`account_id`, `transfer_id`),
    FOREIGN KEY(`account_id`) REFERENCES `accounts`(`address`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO accounts_transfers (account_id, transfer_id)
SELECT account_id, transfer_id FROM accounts_transfers_old;

-- Step 4: Drop the old table
DROP TABLE accounts_transfers_old;

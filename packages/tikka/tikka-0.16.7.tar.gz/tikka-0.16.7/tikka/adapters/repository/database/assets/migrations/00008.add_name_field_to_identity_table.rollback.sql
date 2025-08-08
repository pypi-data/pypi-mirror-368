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
    PRIMARY KEY(`index_`),
    FOREIGN KEY(`address`) REFERENCES `accounts`(`address`) ON DELETE CASCADE
);

-- Step 3: Copy data from the old table
INSERT INTO identities (index_, removable_on, next_creatable_on, status, address, old_address, first_eligible_ud)
SELECT index_, removable_on, next_creatable_on, status, address, old_address, first_eligible_ud FROM identities_old;

-- Step 4: Drop the old table
DROP TABLE identities_old;

-------------------------------------------------------------------

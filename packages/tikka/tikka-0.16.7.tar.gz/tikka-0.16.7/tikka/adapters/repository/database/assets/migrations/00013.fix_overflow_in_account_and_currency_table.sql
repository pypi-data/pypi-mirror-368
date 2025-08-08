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

-- Step 2: Create the new table
CREATE TABLE `currency_new` (
	`code_name`	varchar ( 255 ) NOT NULL UNIQUE,
	`name`	varchar ( 255 ),
	`ss58_format`	integer,
	`token_decimals`	integer DEFAULT null,
	`token_symbol`	varchar ( 255 ) DEFAULT null,
	`universal_dividend` TEXT DEFAULT null,
	`monetary_mass`	TEXT DEFAULT null,
	`members_count`	integer DEFAULT null,
	`block_duration`	integer DEFAULT 6000,
	`epoch_duration`	INTEGER DEFAULT 3600000,
	`certification_number_to_be_member`	integer,
	`minimum_delay_between_two_membership_renewals`	integer,
	`validity_duration_of_membership`	integer,
	`minimum_certifications_received_to_be_certifier`	integer,
	`validity_duration_of_certification`	integer,
	`minimum_delay_between_two_certifications`	integer,
	`maximum_number_of_certifications_per_member`	integer,
	`maximum_distance_in_step`	integer,
	`minimum_percentage_of_remote_referral_members_to_be_member`	integer,
	`identity_automatic_revocation_period`	integer,
	`minimum_delay_between_changing_identity_owner`	integer,
	`confirm_identity_period`	integer,
	`identity_deletion_after_revocation`	integer,
	`minimum_delay_between_identity_creation`	integer,
	`identity_validation_period`	integer,
	`maximum_certifications_per_smith`	integer,
	`number_of_certifications_to_become_smith`	integer,
	`maximum_inactivity_duration_allowed_for_smith`	integer,
	PRIMARY KEY(`code_name`)
);

-- Step 3: Copy data from the old table
INSERT INTO currency_new (
    code_name,
    name,
    ss58_format,
    token_decimals,
    token_symbol,
    universal_dividend,
    monetary_mass,
    members_count,
    block_duration,
    epoch_duration,
    certification_number_to_be_member,
	minimum_delay_between_two_membership_renewals,
	validity_duration_of_membership,
	minimum_certifications_received_to_be_certifier,
	validity_duration_of_certification,
	minimum_delay_between_two_certifications,
	maximum_number_of_certifications_per_member,
	maximum_distance_in_step,
	minimum_percentage_of_remote_referral_members_to_be_member,
	identity_automatic_revocation_period,
	minimum_delay_between_changing_identity_owner,
	confirm_identity_period,
	identity_deletion_after_revocation,
	minimum_delay_between_identity_creation,
	identity_validation_period,
	maximum_certifications_per_smith,
	number_of_certifications_to_become_smith,
	maximum_inactivity_duration_allowed_for_smith
)
SELECT
    code_name,
    name,
    ss58_format,
    token_decimals,
    token_symbol,
    universal_dividend,
    monetary_mass,
    members_count,
    block_duration,
    epoch_duration,
    certification_number_to_be_member,
	minimum_delay_between_two_membership_renewals,
	validity_duration_of_membership,
	minimum_certifications_received_to_be_certifier,
	validity_duration_of_certification,
	minimum_delay_between_two_certifications,
	maximum_number_of_certifications_per_member,
	maximum_distance_in_step,
	minimum_percentage_of_remote_referral_members_to_be_member,
	identity_automatic_revocation_period,
	minimum_delay_between_changing_identity_owner,
	confirm_identity_period,
	identity_deletion_after_revocation,
	minimum_delay_between_identity_creation,
	identity_validation_period,
	maximum_certifications_per_smith,
	number_of_certifications_to_become_smith,
	maximum_inactivity_duration_allowed_for_smith
FROM currency;

-- Step 3: Drop the old table
DROP TABLE currency;

-- Step 4: Rename the new table
ALTER TABLE currency_new RENAME TO currency;

---------------------------------------

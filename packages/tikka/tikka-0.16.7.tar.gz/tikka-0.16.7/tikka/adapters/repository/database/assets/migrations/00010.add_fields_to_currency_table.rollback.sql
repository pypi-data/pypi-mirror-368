-------------------------------------------------------

-- Step 1: Rename the old table
ALTER TABLE currency RENAME TO currency_old;

-- Step 2: Create the new table
create table currency(
    code_name varchar(255) unique primary key not null,
    name varchar(255),
    ss58_format integer,
    token_decimals integer default null,
    token_symbol varchar(255) default null,
    universal_dividend integer default null,
    monetary_mass integer default null,
    members_count integer default null,
    block_duration integer default 6000,
    epoch_duration integer default 3600000
);

-- Step 3: Copy data from the old table
INSERT INTO currency (
    code_name,
    name,
    ss58_format,
    token_decimals,
    token_symbol,
    universal_dividend,
    monetary_mass,
    members_count,
    block_duration,
    epoch_duration
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
    epoch_duration
FROM currency_old;

-- Step 4: Drop the old table
DROP TABLE currency_old;

---------------------------------------

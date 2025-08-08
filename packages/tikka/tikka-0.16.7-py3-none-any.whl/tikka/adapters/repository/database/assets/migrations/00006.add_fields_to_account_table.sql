ALTER TABLE accounts ADD COLUMN total_transfers_count integer not null default 0;
ALTER TABLE accounts ADD COLUMN last_transfer_timestamp timestamp;
ALTER TABLE accounts ADD COLUMN oldest_transfer_timestamp timestamp;

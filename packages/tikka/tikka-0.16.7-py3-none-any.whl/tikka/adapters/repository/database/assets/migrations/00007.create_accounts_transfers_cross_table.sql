create table if not exists accounts_transfers(
    account_id varchar(255) not null,
    transfer_id varchar(255) not null,
    primary key (account_id,transfer_id)
);

create table if not exists technical_committee_members(
        address varchar(255) unique primary key not null,
        identity_index integer,
        identity_name varchar(255)
);

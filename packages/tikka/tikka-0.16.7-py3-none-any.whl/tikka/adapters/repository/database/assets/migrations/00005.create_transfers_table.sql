create table if not exists transfers(
    id varchar(255) unique primary key not null,
    issuer_address varchar(255),
    issuer_identity_index integer,
    issuer_identity_name varchar(255),
    receiver_address varchar(255),
    receiver_identity_index varchar(255),
    receiver_identity_name varchar(255),
    amount integer,
    timestamp timestamp,
    comment varchar(65535) default null,
    comment_type varchar(255) default null
);

create table if not exists technical_committee_proposals(
        hash varchar(255) unique primary key not null,
        call varchar(65535) not null,
        voting varchar(65535) not null
);

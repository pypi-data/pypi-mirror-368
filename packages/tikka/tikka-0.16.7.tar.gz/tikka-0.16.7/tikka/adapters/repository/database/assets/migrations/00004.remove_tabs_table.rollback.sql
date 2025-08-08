create table if not exists tabs(
        id varchar(255) unique primary key not null,
        panel_class varchar(255) not null
);

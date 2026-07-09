alter table users add column pronouns varchar(11) not null default 'they/them';
alter table users alter column pronouns drop default;

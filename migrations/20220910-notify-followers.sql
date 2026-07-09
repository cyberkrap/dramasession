alter table submissions add column notify bool not null default true;
alter table submissions alter column notify drop default;

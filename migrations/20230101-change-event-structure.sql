drop table event_users;
alter table users add column event_darkmode bool;
alter table users alter column event_music drop NOT NULL;

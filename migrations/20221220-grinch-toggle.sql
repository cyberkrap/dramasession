alter table users add column event_music boolean NOT NULL default True;
alter table users alter column event_music drop default;

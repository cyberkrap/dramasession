alter table users alter column background type varchar(40); -- solarpunk/xx.webp ones are 32 chars, plus leave headroom
update users set background='/i/backgrounds/' || background || '.webp' where background is not null;

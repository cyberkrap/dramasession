alter table users add column blacklisted_by int;
alter table users add constraint user_blacklisted_by_fkey foreign key (blacklisted_by) references users(id);

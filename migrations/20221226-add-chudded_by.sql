alter table users add column chudded_by int;
alter table users add constraint user_chudded_by_fkey foreign key (chudded_by) references users(id);
create index fki_user_chudded_by_fkey on users using btree (chudded_by);
update users set chudded_by=1 where agendaposter > 0;

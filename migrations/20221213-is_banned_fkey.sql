alter table users alter column is_banned drop default;
alter table users alter column is_banned drop not null;
update users set is_banned=null where is_banned=0;
create index fki_user_is_banned_fkey on public.users using btree (is_banned);

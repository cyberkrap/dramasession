update users u set shadowbanned=(select id from users f where username=u.shadowbanned) where shadowbanned is not null;
alter table users alter column shadowbanned type int using shadowbanned::integer;
create index fki_user_shadowbanned_fkey on public.users using btree (shadowbanned);
alter table only public.users add constraint user_shadowbanned_fkey foreign key (shadowbanned) references public.users(id);

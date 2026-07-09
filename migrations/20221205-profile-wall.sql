alter table comments add column wall_user_id int;

alter table only comments add constraint wall_user_id_fkey foreign key (wall_user_id) references users(id);

create index fki_wall_user_id_fkey on public.comments using btree (wall_user_id);

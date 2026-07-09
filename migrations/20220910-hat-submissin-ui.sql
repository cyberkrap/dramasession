alter table hat_defs add column submitter_id int;

ALTER TABLE ONLY public.hat_defs
    ADD CONSTRAINT hat_def_submitter_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(id);

CREATE INDEX hat_defs_submitter_id_idx ON public.hat_defs USING btree (submitter_id);

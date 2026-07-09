alter table marseys add column submitter_id int;

ALTER TABLE ONLY public.marseys
    ADD CONSTRAINT marsey_submitter_fkey FOREIGN KEY (submitter_id) REFERENCES public.users(id);

CREATE INDEX marseys_idx4 ON public.marseys USING btree (submitter_id);

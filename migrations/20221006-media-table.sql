CREATE TABLE public.media (
    kind character varying(5) NOT NULL,
    filename character varying(55) NOT NULL,
	user_id Integer NOT NULL,
    created_utc integer NOT NULL,
    size integer NOT NULL
);

ALTER TABLE ONLY public.media
    ADD CONSTRAINT media_pkey PRIMARY KEY (kind, filename);

ALTER TABLE ONLY public.media
    ADD CONSTRAINT media_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

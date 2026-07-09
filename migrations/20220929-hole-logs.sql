CREATE TABLE public.subactions (
    id integer PRIMARY KEY,
	sub character varying(25) NOT NULL,
    user_id integer,
    target_user_id integer,
    target_submission_id integer,
    target_comment_id integer,
    created_utc integer NOT NULL,
    kind character varying(32) DEFAULT NULL::character varying,
    _note character varying(500) DEFAULT NULL::character varying
);

CREATE SEQUENCE public.subactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.subactions_id_seq OWNED BY public.subactions.id;

ALTER TABLE ONLY public.subactions ALTER COLUMN id SET DEFAULT nextval('public.subactions_id_seq'::regclass);

CREATE INDEX fki_subactions_user_fkey ON public.subactions USING btree (target_user_id);

CREATE INDEX modaction_action_idx ON public.subactions USING btree (kind);

CREATE INDEX modaction_pid_idx ON public.subactions USING btree (target_submission_id);

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_submission_fkey FOREIGN KEY (target_submission_id) REFERENCES public.submissions(id);

CREATE INDEX modaction_cid_idx ON public.subactions USING btree (target_comment_id);

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_comment_fkey FOREIGN KEY (target_comment_id) REFERENCES public.comments(id);

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_user_fkey FOREIGN KEY (target_user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.subactions
    ADD CONSTRAINT subactions_sub_fkey FOREIGN KEY (sub) REFERENCES public.subs(name);

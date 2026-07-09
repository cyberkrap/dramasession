CREATE TABLE public.transactions (
    id character varying(36) PRIMARY KEY,
    created_utc integer NOT NULL,
    type character varying(12) NOT NULL,
    amount integer NOT NULL,
    email character varying(255) NOT NULL
);

CREATE INDEX transactions_email_idx ON public.transactions USING btree (email);

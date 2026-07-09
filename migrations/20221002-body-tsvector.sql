ALTER TABLE public.comments ADD COLUMN body_ts tsvector
    GENERATED ALWAYS AS (to_tsvector('english', body)) STORED;
CREATE INDEX comments_body_ts_idx ON public.comments USING GIN (body_ts);

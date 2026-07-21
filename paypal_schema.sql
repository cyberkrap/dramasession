CREATE TABLE IF NOT EXISTS public.paypal_subscriptions (
    subscription_id character varying(64) PRIMARY KEY,
    user_id integer NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    plan_id character varying(64) NOT NULL,
    tier integer NOT NULL,
    status character varying(32) NOT NULL,
    payer_email character varying(320),
    created_utc integer NOT NULL,
    updated_utc integer NOT NULL,
    next_billing_utc integer,
    last_payment_utc integer,
    cancelled_utc integer
);

CREATE INDEX IF NOT EXISTS paypal_subscriptions_user_id_idx ON public.paypal_subscriptions (user_id);
CREATE INDEX IF NOT EXISTS paypal_subscriptions_status_idx ON public.paypal_subscriptions
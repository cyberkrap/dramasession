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
CREATE INDEX IF NOT EXISTS paypal_subscriptions_status_idx ON public.paypal_subscriptions (status);

CREATE TABLE IF NOT EXISTS public.paypal_payments (
    payment_id character varying(128) PRIMARY KEY,
    subscription_id character varying(64) NOT NULL REFERENCES public.paypal_subscriptions(subscription_id) ON DELETE CASCADE,
    user_id integer NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    tier integer NOT NULL,
    gross_cents integer NOT NULL,
    currency character varying(8) NOT NULL,
    status character varying(32) NOT NULL,
    wishbux_granted integer NOT NULL DEFAULT 0,
    created_utc integer NOT NULL,
    updated_utc integer NOT NULL
);

CREATE INDEX IF NOT EXISTS paypal_payments_subscription_id_idx ON public.paypal_payments (subscription_id);
CREATE INDEX IF NOT EXISTS paypal_payments_user_id_idx ON public.paypal_payments (user_id);

CREATE TABLE IF NOT EXISTS public.paypal_webhook_events (
    event_id character varying(128) PRIMARY KEY,
    event_type character varying(128) NOT NULL,
    resource_id character varying(128),
    received_utc integer NOT NULL,
    processed boolean NOT NULL DEFAULT false
);

INSERT INTO public.badge_defs (id, name, description, created_utc)
VALUES (25, 'JIDF Bankroller', 'Contributed at least $100', NULL)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

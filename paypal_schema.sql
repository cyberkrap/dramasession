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

-- Rebrand legacy contribution badges while preserving their IDs and artwork.
UPDATE public.badge_defs SET name = 'Nikki''s Supporter', description = 'Contributed at least $5' WHERE id = 21;
UPDATE public.badge_defs SET name = 'Nikki''s Insider', description = 'Contributed at least $10' WHERE id = 22;
UPDATE public.badge_defs SET name = 'Nikki''s Devoted', description = 'Contributed at least $20' WHERE id = 23;
UPDATE public.badge_defs SET name = 'Nikki''s Obsession', description = 'Contributed at least $50' WHERE id = 24;
UPDATE public.badge_defs SET name = 'Nikki''s Sugar Daddy', description = 'Contributed at least $100' WHERE id = 25;
UPDATE public.badge_defs SET name = 'Nikki''s Bankroller', description = 'Contributed at least $250' WHERE id = 26;
UPDATE public.badge_defs SET name = 'Rich Bich', description = 'Contributed at least $500' WHERE id = 27;

-- Remove the old rDrama currency name from every legacy badge description.
UPDATE public.badge_defs
SET description = replace(replace(description, 'dramacoin', 'Wishcoin'), 'Dramacoin', 'Wishcoin')
WHERE description ILIKE '%dramacoin%';

-- Restore every lifetime contribution milestone already earned from verified payments.
WITH verified_totals AS (
    SELECT user_id, SUM(gross_cents)::bigint AS total_cents
    FROM public.paypal_payments
    WHERE status = 'COMPLETED'
    GROUP BY user_id
), thresholds(threshold_cents, badge_id) AS (
    VALUES
        (500::bigint, 21),
        (1000::bigint, 22),
        (2000::bigint, 23),
        (5000::bigint, 24),
        (10000::bigint, 25),
        (25000::bigint, 26),
        (50000::bigint, 27)
)
INSERT INTO public.badges (user_id, badge_id, created_utc)
SELECT totals.user_id, thresholds.badge_id, EXTRACT(EPOCH FROM NOW())::integer
FROM verified_totals AS totals
CROSS JOIN thresholds
WHERE totals.total_cents >= thresholds.threshold_cents
ON CONFLICT DO NOTHING;
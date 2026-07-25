# Live PayPal checkout deployment

The production support page now defaults to PayPal's live environment and ignores the old generic sandbox variables.

## 1. Create the live PayPal app

In the PayPal Developer Dashboard, switch from **Sandbox** to **Live** and create or open the REST application used by The Obsession Club.

Do not place the client secret in source control or chat. Store it only in Railway's environment variables.

## 2. Create the live subscription plans

Create five active monthly plans in USD with these exact recurring prices:

| Railway suffix | Tier | Monthly amount |
| --- | --- | ---: |
| `SUPPORTER` | Nikki's Supporter | $5 |
| `INSIDER` | Bear's Insider | $10 |
| `DEVOTED` | Sandy's Devoted | $20 |
| `OBSESSED` | Curry's Obsession | $50 |
| `INNER_CIRCLE` | Ian's Bankroller | $100 |

Each plan ID must come from the **Live** dashboard, not Sandbox.

## 3. Add the live webhook

Create a webhook on the live REST app with this URL:

`https://theobsessionclub.com/api/paypal/webhook`

Subscribe it to the subscription and sale events used by the application:

- `BILLING.SUBSCRIPTION.ACTIVATED`
- `BILLING.SUBSCRIPTION.UPDATED`
- `BILLING.SUBSCRIPTION.CANCELLED`
- `BILLING.SUBSCRIPTION.EXPIRED`
- `BILLING.SUBSCRIPTION.SUSPENDED`
- `BILLING.SUBSCRIPTION.PAYMENT.FAILED`
- `PAYMENT.SALE.COMPLETED`
- `PAYMENT.SALE.REFUNDED`
- `PAYMENT.SALE.REVERSED`

## 4. Configure Railway

Set these variables on the production service:

```text
PAYPAL_MODE=live
PAYPAL_CURRENCY=USD
PAYPAL_LIVE_CLIENT_ID=<live REST app client ID>
PAYPAL_LIVE_CLIENT_SECRET=<live REST app secret>
PAYPAL_LIVE_WEBHOOK_ID=<live webhook ID>
PAYPAL_LIVE_PLAN_SUPPORTER=<live $5 plan ID>
PAYPAL_LIVE_PLAN_INSIDER=<live $10 plan ID>
PAYPAL_LIVE_PLAN_DEVOTED=<live $20 plan ID>
PAYPAL_LIVE_PLAN_OBSESSED=<live $50 plan ID>
PAYPAL_LIVE_PLAN_INNER_CIRCLE=<live $100 plan ID>
```

The previous generic variables such as `PAYPAL_CLIENT_ID` and `PAYPAL_PLAN_SUPPORTER` are intentionally ignored in live mode so sandbox credentials cannot accidentally reach production checkout.

## 5. Deploy and verify

After Railway redeploys:

1. Open `/donate` while signed in.
2. Confirm the page says **Live PayPal checkout is ready**.
3. Complete one real $5 subscription using a normal PayPal buyer account.
4. Confirm the payment appears in the PayPal Live dashboard.
5. Confirm the site records the subscription, grants the correct Wishbux and supporter benefits, and processes cancellation from the support page.

The application does not grant benefits from browser approval alone. It verifies the subscription and completed transaction through PayPal's live API and signed webhook before fulfillment.

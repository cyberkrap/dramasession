(() => {
    'use strict';

    const configElement = document.getElementById('paypal-support-config');
    const messageElement = document.getElementById('paypal-checkout-message');
    if (!configElement) return;

    let config;
    try {
        config = JSON.parse(configElement.textContent);
    } catch (_error) {
        return;
    }

    function showMessage(message, isError = false) {
        if (!messageElement) return;
        messageElement.hidden = false;
        messageElement.classList.toggle('support-checkout-message-error', isError);
        messageElement.textContent = message;
    }

    if (!window.paypal || typeof window.paypal.Buttons !== 'function') {
        showMessage('PayPal checkout could not load. Refresh the page and try again.', true);
        return;
    }

    document.querySelectorAll('.support-paypal-button[data-plan-id]').forEach(container => {
        const planId = container.dataset.planId;
        const tierName = container.dataset.tierName || 'support';
        if (!planId) return;

        window.paypal.Buttons({
            style: {
                layout: 'vertical',
                shape: 'pill',
                color: 'white',
                label: 'subscribe',
                height: 44
            },
            createSubscription(_data, actions) {
                showMessage(`Opening PayPal for the ${tierName} tier...`);
                return actions.subscription.create({
                    plan_id: planId,
                    custom_id: config.customId,
                    application_context: {
                        shipping_preference: 'NO_SHIPPING',
                        user_action: 'SUBSCRIBE_NOW'
                    }
                });
            },
            async onApprove(data) {
                showMessage('PayPal approved the subscription. Verifying the payment...');
                try {
                    const body = new URLSearchParams({
                        formkey: config.formkey,
                        subscription_id: data.subscriptionID
                    });
                    const response = await fetch(config.confirmUrl, {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body
                    });
                    const result = await response.json().catch(() => ({}));
                    if (!response.ok || !result.ok) {
                        throw new Error(result.error || 'The server could not verify this subscription.');
                    }
                    showMessage(result.message || 'Subscription verified.');
                    window.setTimeout(() => window.location.assign('/donate?payment=success'), 1200);
                } catch (error) {
                    showMessage(error.message || 'Subscription verification failed. Contact the administrators with your PayPal subscription ID.', true);
                }
            },
            onCancel() {
                showMessage('PayPal checkout was cancelled. No subscription was created.');
            },
            onError(error) {
                console.error('PayPal subscription error', error);
                showMessage('PayPal checkout failed. Refresh the page and try again.', true);
            }
        }).render(`#${container.id}`).catch(error => {
            console.error('PayPal button render error', error);
            showMessage('A PayPal button could not load. Refresh the page and try again.', true);
        });
    });
})();
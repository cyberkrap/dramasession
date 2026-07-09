'use strict';

function urlB64ToUint8Array(base64String) {
	const padding = '='.repeat((4 - base64String.length % 4) % 4);
	const base64 = (base64String + padding)
		.replace(/\-/g, '+')
		.replace(/_/g, '/');

	const rawData = window.atob(base64);
	const outputArray = new Uint8Array(rawData.length);

	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}

function updateSubscriptionOnServer(subscription, apiEndpoint) {
	const formData = new FormData();
	formData.append("subscription_json", JSON.stringify(subscription));

	const xhr = createXhrWithFormKey(
		apiEndpoint,
		'POST',
		formData
	);

	xhr[0].send(xhr[1]);
}

function subscribeUser(swRegistration, applicationServerPublicKey, apiEndpoint) {
	const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
	swRegistration.pushManager.subscribe({
		userVisibleOnly: true,
		applicationServerKey: applicationServerKey
	})
	.then(function(subscription) {
		return updateSubscriptionOnServer(subscription, apiEndpoint);

	})
	.then(function(response) {
		if (!response.ok) {
			throw new Error('Bad status code from server.');
		}
		return response.json();
	})
	.then(function(responseData) {
		if (responseData.status!=="success") {
			throw new Error('Bad response from server.');
		}
	})
	.catch(function() {
	});
}

function registerServiceWorker(serviceWorkerUrl, applicationServerPublicKey, apiEndpoint){
	let swRegistration = null;
	if ('serviceWorker' in navigator && 'PushManager' in window) {
		navigator.serviceWorker.register(serviceWorkerUrl)
		.then(function(swReg) {
			subscribeUser(swReg, applicationServerPublicKey, apiEndpoint);

			swRegistration = swReg;
		})
		.catch(function() {
		});
	} else {
	}
	return swRegistration;
}

registerServiceWorker(
	"/assets/js/service_worker.js",
	document.getElementById('VAPID_PUBLIC_KEY').value,
	"/push_subscribe"
)

// Based On https://github.com/chrisdavidmills/push-api-demo/blob/283df97baf49a9e67705ed08354238b83ba7e9d3/main.js

var isPushEnabled = false,
    registration;



window.addEventListener('load', function() {
    // Do everything if the Browser Supports Service Worker
    if ('serviceWorker' in navigator) {
        const serviceWorker = document.querySelector('meta[name="service-worker-js"]').content;
        navigator.serviceWorker.register(serviceWorker).then(
        function(reg) {
            registration = reg;
            initialiseState(reg);
        });
    }
  // If service worker not supported, show warning to the message box
    else {
        showMessage(gettext('Service workers no son soportados en este navegador.'));
    }

  // Once the service worker is registered set the initial state
    function initialiseState(reg) {
        // Are Notifications supported in the service worker?
        if (!(reg.showNotification)) {
            showMessage(gettext('Las notificaciones no son soportadas en este navegador.'));
            return;
        }

        // Check the current Notification permission.
        // If its denied, it's a permanent block until the
        // user changes the permission
        if (Notification.permission === 'denied') {
            // Show a message and activate the button
            // console.log("Notificaciones denegadas");
            showMessage(gettext('Las notificaciones están bloqueadas en este navegador.'));
            return;
        }

        // Check if push messaging is supported
        if (!('PushManager' in window)) {
            // Show a message and activate the button
            showMessage(gettext('Las notificaciones no están disponibles en este navegador.'));
            return;
        }

    // We need to get subscription state for push notifications and send the information to server
        reg.pushManager.getSubscription().then(
            function(subscription) {
                if (subscription){
                    postSubscribeObj('subscribe', subscription,
                        function(response) {
                            // Check the information is saved successfully into server
                            if (response.status === 201) {
                                // Show unsubscribe button instead
                                isPushEnabled = true;
                                showMessage(gettext('Notificaciones habilitadas correctamente'));
                            }
                        }
                    );
                }
                else{
                    try{
                        setTimeout(function(){
                            subscribe(reg)
                        }, 5000);
                    } catch (e) {
                        console.log(e)
                    }
                }
            }
        );
    }
});

function showMessage(message) {
    const messageBox = document.getElementById('webpush-message');
    if (messageBox) {
        messageBox.textContent = message;
        messageBox.style.display = 'block';
    }
}

function subscribe(reg) {
  // Get the Subscription or register one
    reg.pushManager.getSubscription().then(
        function(subscription) {
            var metaObj, applicationServerKey, options;
            // Check if Subscription is available
            if (subscription) {
                return subscription;
            }

            metaObj = document.querySelector('meta[name="django-webpush-vapid-key"]');
            applicationServerKey = metaObj.content;
            options = {
                userVisibleOnly: true
            };
            if (applicationServerKey){
                options.applicationServerKey = urlB64ToUint8Array(applicationServerKey)
            }
            // If not, register one
            reg.pushManager.subscribe(options)
            .then(
            function(subscription) {
                postSubscribeObj('subscribe', subscription,
                function(response) {
                    // Check the information is saved successfully into server
                    if (response.status === 201) {
                        // Show unsubscribe button instead
                        isPushEnabled = true;
                        showMessage(gettext('Notificaciones habilitadas correctamente'));
                    }
                });
            })
            .catch(
                function() {
                    // console.log(gettext('Error mientras se activaban las notificaciones 1'), arguments)
                }
            )
        }
    );
}

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (var i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

function unsubscribe(reg) {
  // Get the Subscription to unregister
  reg.pushManager.getSubscription()
    .then(
      function(subscription) {

        // Check we have a subscription to unsubscribe
        if (!subscription) {
          // No subscription object, so set the state
          // to allow the user to subscribe to push
            showMessage(gettext('Subcrición no está disponible'));
            return;
        }
        postSubscribeObj('unsubscribe', subscription,
          function(response) {
            // Check if the information is deleted from server
            if (response.status === 202) {
              // Get the Subscription
              // Remove the subscriptionn
              
              subscription.unsubscribe()
                .then(
                    function(successful) {
                        showMessage(gettext('Notificaciones desactivadas correctamente'));
                        isPushEnabled = false;
                    }
                )
                .catch(
                    function(error) {
                        showMessage(gettext('Error mientras se desactivaban las notificaciones 2'));
                    }
                );
            }
          });
      }
    )
}

function postSubscribeObj(statusType, subscription, callback) {
  // Send the information to the server with fetch API.
  // the type of the request, the name of the user subscribing,
  // and the push subscription endpoint + key the server needs
  // to send push messages

    var browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase(),
    user_agent = navigator.userAgent,
    data =  {   status_type: statusType,
                subscription: subscription.toJSON(),
                browser: browser,
                user_agent: user_agent,
                group: group_name_webpush || "Main",
            };

    fetch("/webpush/save_information", {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
            credentials: 'include'
    }).then(callback);
}
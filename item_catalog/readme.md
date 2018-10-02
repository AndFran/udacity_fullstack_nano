

**Introduction:

A CRUD application using pure flask (no extensions)
Allows the authenticated user to create categories and add, delete and update items.
Only the creator of an item can update or delete them.

Users can authenticate with OAUTH through google plus, or by a simple username and password combination.
Users can manage their accounts in the "My Account" Menu.

Each form that is posted is protected against CSRF attacks.


**Setup Instructions:

The application will run as is after you install the dependencies:

- sqlalchemy
- flask
- oauth2client

However, if you want to allow oauth2 authorization you will need to register the app
in:

https://console.cloud.google.com/apis

and obtain a valid client secret.json file (see google guides for details).
This will give you a valid: client_id and client_secret

                **You must keep your client_secret SECRET**


The json file should be called: client_secret.json and placed in the projects route folder.

If you want to rename the file you will need to change the following line in app.py:

CLIENT_SECRETS_FILE = 'YOUR_NEW_SECRETS_FILE.json'


Also notice the following:


if __name__ == '__main__':
    app.secret_key = "TODO CHANGE THIS TO TOP SECRET KEY"
    app.run(host="localhost", port=5000, debug=True, threaded=False)

            **app.secret_key should be set to a random secret key that is kept SECRET as it is used
                        to sign session cookies.  **

Notice we explicitly set: host="localhost" and port=5000 this is because google OAUTH does
not currently allow IPs to be placed in the valid domains.

Remove debug=True if deploying to a production environment so that no information about the
applications state is leaked.

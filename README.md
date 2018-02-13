# Giftr
An app to give away the stuff you don't use or to receive other people's stuff.
It's a simple catalog of gifts. Want it? Claim it. The "gifter" will then be able to see a list of people who claimed it, along with their message.

## Installation
* Clone this repository: `git clone https://github.com/Zinston/giftr`
* Install dependencies: `pip install -r requirements.txt`
* Configure a project for [Facebook Sign-In](https://developers.facebook.com/products/account-creation) (don't forget to set it up for http://localhost:8080)
* Save your Facebook credentials in a `fb_client_secrets.json` file in the root directory, with the following form:
    {
	 "web": {
			 "app_id": "YOUR_APP_ID",
			 "app_secret": "YOUR_APP_SECRET"
			}
	}
* Configure a project for [Google Sign-In](https://developers.google.com/identity/sign-in/web/sign-in) (don't forget to set it up for http://localhost:8080)
* Download your Google credentials and save them in a `google_client_secrets.json` file in the root directory. They should have the following form:
    {
     "web": {
     		 "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
     		 "project_id":"YOUR_PROJECT_ID",
     		 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     		 "token_uri":"https://accounts.google.com/o/oauth2/token",
     		 "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     		 "client_secret": "YOUR_CLIENT_SECRET",
     		 "redirect_uris": ["http://localhost:8080"]
     		}
    }
* Run the app with python 2.7: `python views.py`
* It's running on http://localhost:8080

## Limitations
No functionality has been implemented yet to:

* locate users (although the User table is ready with an address row)
* accept/reject claims
* contact users
* notify users of claims

## Contributing
Ideas, contributions and improvements are more than welcome. When adding a feature, please create a separate topic branch and first look at the Issues to find out if someone else is working on it already.

## License
_Giftr_ is released under the [Apache License 2.0](/LICENSE).

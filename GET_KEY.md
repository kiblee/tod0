Getting your own API key
------------------------

You need to get your own Microsoft API key to use `tod0`. 
  1. Sign in to the [Azure portal](https://portal.azure.com/) using a Microsoft account.
  2. In the left-hand navigation pane, select the `Azure Active Directory` service, and then select `App registrations > New registration`.
  3. When the Register an application page appears, enter your application's registration information:
     - Name: `tod0`
     - Supported account types: `Accounts in any organizational directory and personal Microsoft accounts`
     - Platform configuration: `Client Application`
  4. Click `Register` when finished.
  5. You will be redirected to the app's authentication page. Under `Platform configurations` click `Add a platform`. 
  6. Select `Web` and enter `https://localhost/login/authorized` for the `Redirect URI` and click `Configure`.
  
  7. Next, in the left-hand navigation pane, select `Certificates & secrets`.
  6. Click `New client secret` and create a secret key. You may use any description. Click `Add`. Make sure to copy the secret key somewhere before leaving the page as you will not be able to view it again.
  7. In the left-hand navigation pane, select `Overview`. Copy the `application (client) id` and the `secret key` from the previous step to `~/.config/tod0/keys.yml` like so: 
  
    client_id: '1234abcd-abc-etc-etc'
    client_secret: 'ABCD-abcd-etc-etc'

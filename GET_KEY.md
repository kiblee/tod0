Getting your own API key
------------------------

You need to get your own Microsoft API key to use `tod0`. 
  1. Sign in to the [Azure portal](https://portal.azure.com/).
  2. In the left-hand navigation pane, select the `Azure Active Directory` service, click `Add` -> `App registration` at the top. 
  3. When the `Register an application` page appears, enter your application's registration information:
     - Name: `tod0`
     - Supported account types: `Accounts in any organizational directory and personal Microsoft accounts`
     - Redirect URI: `Web` - `https://localhost/login/authorized`
  4. Click `Register` when finished and note the `Application (client) ID`.
  5. Next, click `Add a certificate or secret`
  6. Click `New client secret` and create a secret key. You may use any description. Click `Add`.
  7. Copy the `Application (client) ID` and the `Secret Value` from the previous steps to `~/.config/tod0/keys.yml` like so: 
  
    client_id: '1234abcd-abc-etc-etc'
    client_secret: 'ABCD-abcd-etc-etc'

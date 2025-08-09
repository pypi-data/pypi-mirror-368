import requests
import time
import subprocess
import abc
import requests_gssapi
import bs4
import urllib
import uuid
import os
import json
import logging
import inputimeout
from authlib.oauth2.rfc7636 import create_s256_code_challenge
from authlib.common.security import generate_token
from authlib.jose import JsonWebKey,JsonWebToken
from authlib.oidc.core import IDToken
import authlib.jose


"""
This package allows us to retrieve OIDC tokens from the CERN SSO. It was then expanded to handle session cookie 
based authentication.

There are two main classes of authentication supported: Token and Session based auth
token: 
    passes a bearer token in the Authorization header
session cookie:
    emulates a browser session and passes the session cookies in the request

A common base class AuthBase defines the interface, it has currently one public method: authparams
This will return a dictionary which can be passed to the requests library to authenticate the request

There are two further base classes AuthTokenBase and AuthSessionBase which define the interface for token and 
session based auth respectively

TokenAuthBase has the following public methods in addition to those of AuthBase:
 
  token(): returns the access token acquiring it first if necessary
  headers(): returns the necessary headers to make a request to an api which accepts said token

There is also a helper function parse_token which will parse a token into an authlib.oidc.core.IDToken, 
its claims are accessed by ["key"] and can printed directly

It has the ability to store a token for later use in a file, this is most useful for the device auth flow and folks 
with 2FA

There are various ways of authenticating which is handled by the specific derived class. There are two main types
application auth: where we log in as an application registered with the CERN SSO
user auth: where we log in as a user (or service account, basically soemthing with cern account)

The authentication methods are as follows:
ClientAuth: application auth, this authenticates using a client id and secret
KerbAuth: user auth, this authenticates using kerberos
AuthGetSSOTokenAuth: user auth, this authenticates using auth-get-sso-token
DeviceAuth: user auth, this authenticates using the device authorization flow

SessionAuthBase has the following public methods in addition to those of AuthBase:
    cookies(): returns the session cookies acquiring them first if necessary
    session(): returns the authentication session, initializing it first if necessary

KerbSessionAuth: user auth, this authenticates using kerberos and uses session cookies

The following environmental variables control settings
TSGAUTH_LOGLEVEL : logging level ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
TSGAUTH_AUTHDIR : directory where the auth files are written if requested to be (default: ~/.tsgauth)) 
TSGAUTH_FORCE_USE_AUTHFILE : forces the authfile to be written/used (set to 1 to do this)
TSGAUTH_FORCE_DONT_USE_AUTHFILE : forces the authfile to not be written/used  (set to 1 do this)
TSGAUTH_ALLOWED_ALGS : the allowed algorithms for the token, unset defaults to RS256, can be set to "ALL" to allow all algorithms or a comma separated list of allowed algorithms (the default avoids the risk of signature bypass described in CVE-2016-10555 which 'ALL' would be vulnerable to)

author: Sam Harper (RAL) 2022

"""


def _setup_logging():
    logging_lvl = os.environ.get("TSGAUTH_LOGLEVEL", "ERROR")
    if logging_lvl not in ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(
            f"env 'TSGAUTH_LOGLEVEL' must be one of NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL, got {logging_lvl}\nPlease either unset it or set to one of those values"
        )
    logging.getLogger(__name__).setLevel(logging_lvl)
    logging.getLogger(__name__).addHandler(logging.StreamHandler())


_setup_logging()


def parse_token(
    token,
    jwks_url="https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs",
    issuer="https://auth.cern.ch/auth/realms/cern",
    client_id=None,
    validate=True,
    jwks_key=None,
):
    """
    parses a token (optionally validated) into an authlib.oidc.core.IDToken, its claims are accessed by key() and can printed directly

    :param token: the token to parse
    :jwks_url: the url from which to obtain the the json web key sets to verify and decode the token
               used if jwks_certs is None
    :issuer: the issuer of token for validation purposes
    :client_id: the client id this token is for (aud) for validation purposes
    :validate: whether to validate the token
    :jwks_key: the json web key set to verify and decode the token, defaults None 
                 if None, it will be obtained from jwks_url
    :returns: the parsed token as an authlib.oidc.core.IDToken
    :rtype: authlib.oidc.core.IDToken
    """

    """
    here we limit our allowed algorithms to RS256 to avoid the risk of
    signature bypass described in CVE-2016-10555

    by default we just allow RS256, but this can be overriden by setting the env variable 
    TSGAUTH_ALLOWED_ALGS to "ALL" to allow all algorithms or a comma separated list of allowed algorithms
    """
    allowed_algs = os.environ.get("TSGAUTH_ALLOWED_ALGS",None)
    if allowed_algs is None:
        jwt = JsonWebToken(['RS256'])
    elif allowed_algs.upper() != "ALL":
        jwt = JsonWebToken(allowed_algs.split(","))
    else:
        jwt = authlib.jose.jwt  
    def load_key(header, payload):   
        if jwks_key is not None:
            return JsonWebKey.import_key(jwks_key, header)
        else:     
            jwks_certs = requests.get(jwks_url).json()         
            return JsonWebKey.import_key(jwks_certs["keys"][0], header)

    claims_cls = IDToken
    claims_options = {}
    if issuer:
        claims_options["iss"] = {"values": [issuer]}
    if client_id:
        claims_options["aud"] = {"values": [client_id]}

    claims = jwt.decode(
        token,
        key=load_key,
        claims_cls=claims_cls,
        claims_options=claims_options,
    )
    if validate:
        claims.validate(leeway=120)
    return claims


def token_exchange(client_id, target_client_id, token, token_url, client_secret=None):
    """
    does a simple token swap, this is how you go from one audience (or client_id) to another
    note: the target_client_id must have given the client_id exchange permissions in the application portal
    :param client_id: the client id of the token to exchange
    :param target_client_id: the client id of the token to exchange to
    :param token: the token to exchange
    :param token_url: the url of the token exchange endpoint
    :returns: the token response from the auth server
    :raises AuthError: incase of unsuccessful token exchange
    """

    r = requests.post(
        token_url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "audience": target_client_id,
            "subject_token": token,
        },
    )
    if "access_token" in r.json():
        return r.json()
    else:
        raise AuthError(
            f"""The following error occured when exchanging the token                            
                        {r.text}                                                        
                        """
        )


class KerbLogin:
    def __init__(self, url=None, authhostname="auth.cern.ch", authrealm="cern"):
        if url == None:
            url = f"https://twiki.cern.ch/twiki/bin/viewauth/CMS/TriggerStudies"
        self.session, self.response = self.login(url, authhostname, authrealm)

    @staticmethod
    def _parse_login_err_msg(text):
        """
        parses the error message from the CERN login page
        code is heavily borrowed from https://gitlab.cern.ch/authzsvc/tools/auth-get-sso-cookie/

        :param text: html text with err msg to parse
        """
        err_page = bs4.BeautifulSoup(text, features="html.parser")
        err_msg = err_page.find(id="kc-error-message")
        if not err_msg:
            return "no error message found, not sure what to suggest, maybe try DeviceAuth"
        else:
            return err_msg.find("p").text

    @staticmethod
    def login(url, authhostname="auth.cern.ch", authrealm="cern"):
        """
        requests and saves a token from the issuer (eg the CERN SSO service)
        throws an exception AuthError if it was not successful

        code is heavily borrowed from https://gitlab.cern.ch/authzsvc/tools/auth-get-sso-cookie/
        """
        if url == None:
            url = f"https://twiki.cern.ch/twiki/bin/viewauth/CMS/TriggerStudies"
        session = requests.Session()
        # this will return us the log in page which gives us the uris needed to log in , specifically it gives us the session_code for the auth session we have initiated
        # unfortunately its a webpage so we need to parse the url (really its the session_code in the url we need, everything else is known)
        # I feel there must be an API to do this but so far havent found it
        r_login = session.get(url)
        r_login_url_parsed = urllib.parse.urlparse(r_login.url)
        if r_login_url_parsed.netloc != authhostname:
            logging.getLogger(__name__).info(
                "not a CERN SSO protected page", r_login.url
            )
            return session, r_login
        soup = bs4.BeautifulSoup(r_login.text, features="html.parser")
        kerb_button = soup.find(id="social-kerberos")
        if not kerb_button:
            raise AuthError(
                f"Issue with the log on page, no kerb option\nstatus code: {r_login.status_code}\nerror msg:{KerbLogin._parse_login_err_msg(r_login.text)}"
            )
        kerb_url = f"https://{authhostname}{kerb_button.get('href')}"
        r_kerb = session.get(kerb_url)
        r_auth = session.get(
            r_kerb.url,
            auth=requests_gssapi.HTTPSPNEGOAuth(
                mutual_authentication=requests_gssapi.OPTIONAL
            ),
            allow_redirects=False,
        )

        while (
            r_auth.status_code == 302 and r_auth.headers["Location"].startswith(f"https://{authhostname}")
        ):
            r_auth = session.get(r_auth.headers["Location"], allow_redirects=False)

        twofa_try_count = 0
        twofa_max_tries = 3
        while r_auth.status_code != 302 and twofa_try_count < twofa_max_tries:
            twofa_try_count += 1
            auth_soup = bs4.BeautifulSoup(r_auth.text, features="html.parser")
            twofa_form = auth_soup.find(id="kc-otp-login-form")
            if twofa_form != None:
                twofa_params = urllib.parse.parse_qs(
                    urllib.parse.urlparse(twofa_form["action"]).query
                )
                twofa_url = f"https://{authhostname}/auth/realms/{authrealm}/login-actions/post-broker-login"
                try:
                    twofa_code = inputimeout.inputimeout(
                        prompt=f"Please enter your 2fa code (try {twofa_try_count} / {twofa_max_tries}):\n",
                        timeout=60 * 5,
                    )
                except inputimeout.TimeoutOccurred:
                    raise AuthError("timeout expired waiting for 2fa code (5mins)")
                r_auth = session.post(
                    twofa_url,
                    params=twofa_params,
                    data={"otp": twofa_code},
                    allow_redirects=False,
                )
                while (
                    r_auth.status_code == 302
                    and r_auth.headers["Location"].startswith(f"https://{authhostname}")
                ):                    
                    r_auth = session.get(
                        r_auth.headers["Location"], allow_redirects=False
                    )
            else:
                break  # not a 2fa request, there is an actual error

        if r_auth.status_code != 302:
            if twofa_try_count >= twofa_max_tries:
                raise AuthError(f"2fa failed too many times, error msg {r_auth.text}")
            else:
                raise AuthError(
                    f"Login failed, error msg {KerbLogin._parse_login_err_msg(r_auth.text)}"
                )

        return session, r_auth


class AuthError(Exception):
    pass

class FilePermissionsError(Exception):
    pass

class AuthBase(abc.ABC):
    """
    Abstract base class for general authentication which handles common functionality for all authentication methods

    It offers only one method to the user "authparams" which is a dictionary intended to be passed to the requests library
    This means it can handle session cookie based auth or token based auth with one function

    In the future it will also supply a  session() and a request() method which will return session and request objects already setup for authentication

    From an internals perspective, it also handles the saving and loading of tokens / cookies from files if requested
    """

    def __init__(self, hostname="auth.cern.ch", realm="cern", use_auth_file=False):
        """
        :param hostname: the hostname of the authentication service (default: auth.cern.ch)
        :param realm: the realm of the authentication service (default: cern)
        :param use_auth_file: if true, the auth information is stored in a file and reused if possible
        """
        self.hostname = hostname
        self.realm = realm
        self.use_auth_file = use_auth_file 
        force_use = int(os.environ.get("TSGAUTH_FORCE_USE_AUTHFILE", 0))
        force_dont = int(os.environ.get("TSGAUTH_FORCE_DONT_USE_AUTHFILE", 0))
        if force_use and force_dont:
            raise ValueError(
                "TSGAUTH_FORCE_USE_AUTHFILE and TSGAUTH_FORCE_DONT_USE_AUTHFILE are both set to true, please unset/set to false one of them to continue"
            )
        elif force_use:
            self.use_auth_file = True
            logging.getLogger(__name__).info(
                f"forcing use of auth file for persistent sessions"
            )
        elif force_dont:
            self.use_auth_file = False
            logging.getLogger(__name__).info(
                f"forcing disabling use of auth file so no persistent sessions"
            )        

    def _get_auth_dir(self):
        auth_dir = os.path.expanduser(os.environ.get("TSGAUTH_AUTHDIR","~/.tsgauth"))
        logging.getLogger(__name__).info(
                f"using auth dir {auth_dir} to store authentication files"
        )
        if not os.path.exists(auth_dir):
            try:
                os.makedirs(auth_dir, mode=0o700)
                return auth_dir
            except Exception as e:
                logging.getLogger(__name__).warning(
                    f"error creating auth dir {auth_dir}\nerror:\n {e}"
                )
                return None

        elif not os.path.isdir(auth_dir):
            logging.getLogger(__name__).warning(
                f"specified directory for auth {auth_dir} exists and is not a directory"
            )
            return None
        else:
            return auth_dir

    def _get_auth_path(self):
        """
        returns the full path to the authentication file
        """
        auth_dir = self._get_auth_dir()
        if auth_dir is not None:
            return os.path.join(auth_dir, self._get_auth_filename())
        else:
            return None

    @abc.abstractmethod
    def _get_auth_filename(self):
        """
        this should be overwritten by derived classes
        this is because tokens are named with their client id and session cookies are with just cookies
        """
        pass

    def _read_auth_from_file(self):
        filename = self._get_auth_path()
        try:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"error reading auth from file {filename}\nerror:\n {e}"
            )
            return None

    def _write_auth_to_file(self):
        filename = self._get_auth_path()        
        try:
            def opener(path, flags):
                return os.open(path, flags, mode=0o600)
            with open(filename, "w",opener=opener) as f:
                permissions = oct(os.stat(filename).st_mode)[-3:]
                if permissions != "600":
                    raise FilePermissionsError(
                        f"permissions on auth file {filename} are {permissions}, this is not secure, please change to 600 either by chmod or by removing it and letting  tsgauth recreate it"
                    )                                
                json.dump(self._get_auth_json_repr(), f)
        except FilePermissionsError as e:
            raise e
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"error writing auth to file {filename}\nerror:\n {e}"
            )

    @abc.abstractmethod
    def _get_auth_json_repr(self):
        """
        the json represenation of the auth data to store, again different for tokens and session cookies
        """
        pass

    @abc.abstractmethod
    def authparams(self, headers=None):
        """
        returns a dictionary of the necessary parameters for requests to authenticate
        intended to be passed in a r = requests.get(url,**authparams())
        currently this will be either cookies or headers depending on the type
        :params headers: any extra headers to add to the request
        """
        pass


class SessionAuthBase(AuthBase, abc.ABC):
    def __init__(self, hostname="auth.cern.ch", realm="cern", use_auth_file=False):
        super().__init__(hostname=hostname, realm=realm, use_auth_file=use_auth_file)
        self._authsession = None

    def cookies(self):
        """
        returns the auth session cookies
        """
        self._set_authsession()
        return self._authsession.cookies

    def session(self):
        """
        returns the auth session
        """
        self._set_authsession()
        return self._authsession

    def authparams(self, headers=None):
        """
        returns the auth parameters, this is a dictionary which can be passed to the requests library
        for session auth, this is just cookies
        """
        self._set_authsession()
        if headers == None:
            return {"cookies": self._authsession.cookies}
        else:
            return {"cookies": self._authsession.cookies, "headers": dict(headers)}

    def _set_authsession(self):
        """
        starts an authentication session if one does not already exist
        otherwise renews the session if it is close to expiry
        or reads it from file if use_auth_file is True
        """

        if self._authsession == None and self.use_auth_file:
            cookie_list = self._read_auth_from_file()

            if cookie_list:
                self._authsession = requests.Session()
                for cookie in cookie_list:
                    self._authsession.cookies.set(**cookie)
                logging.getLogger(__name__).info(
                    f"cookies read from file, expires in {self._session_expiry_in()}"
                )

        if self._session_expiry_in() < 60 * 5:  # 5mins
            logging.getLogger(__name__).debug(
                f"renewing auth session due to expiry in {self._session_expiry_in()}"
            )
            self._set_authsession_impl()
            self._write_auth_to_file()

    def _get_auth_filename(self):
        """
        specifies the name of the file to store the auth session in
        """
        return "authsession.json"

    def _get_auth_json_repr(self):
        """
        returns the json representation of the session cookies
        """
        return [
            {
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
                "expires": c.expires,
            }
            for c in self._authsession.cookies
        ]

    def _session_expiry_in(self):
        if self._authsession != None:
            for cookie in self._authsession.cookies:
                if (
                    cookie.name == "KEYCLOAK_SESSION"
                    and cookie.domain == self.hostname
                    and cookie.path == f"/auth/realms/{self.realm}/"
                ):
                    return cookie.expires - time.time()

        return 0

    @abc.abstractmethod
    def _set_authsession_impl(self):
        """
        derived classes should define this method to initiate the auth session
        it is assumed that the checks that this needs to be done are already done
        """
        pass


class TokenAuthBase(AuthBase, abc.ABC):
    """
    base class for authenticating with the CERN SSO using the oidc standard
    the resulting token is accessable via token() and a helper function headers() supplies the necessary headers
    to pass this to an api request

    child classes are intended to define the _set_token_impl method to actually retrieve the token via a concrete authentication method

    if authentication fails, an AuthError is thrown

    """

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        target_client_id=None,
        hostname="auth.cern.ch",
        realm="cern",
        use_auth_file=False,
    ):
        """
        :param client_id: the client id of the application to authenticate as
        :param client_secret: the client secret of the application to authenticate as
        :param target_client_id: the client id of the application to request the token for, also know as the audience
        :param hostname: the hostname of the authentication service (default: auth.cern.ch)
        :param realm: the realm of the authentication service (default: cern)
        :param use_auth_file: whether to save the auth credentials to file for reuse
        """
        super().__init__(hostname=hostname, realm=realm, use_auth_file=use_auth_file)
        self._token_response = None
        self._token_iat = None
        self._token_exp = None
        self._token_required_remaining_time = 20 #seconds, here for testing mostly
        self.client_id = client_id
        self.client_secret = client_secret
        self.target_client_id = target_client_id
        self.token_url = (
            f"https://{hostname}/auth/realms/{realm}/protocol/openid-connect/token"
        )
        self.api_access_token_url = (
            f"https://{hostname}/auth/realms/{realm}/api-access/token"
        )
        self.device_auth_url = f"https://{hostname}/auth/realms/{realm}/protocol/openid-connect/auth/device"
        self.auth_url = (
            f"https://{hostname}/auth/realms/{realm}/protocol/openid-connect/auth"
        )
        self.jwks_url = (
            f"https://{hostname}/auth/realms/{realm}/protocol/openid-connect/certs"
        )

    def _refresh_token(self):
        """
        determines if the token needs to be refreshed and if so, refreshes it
        :returns: True if the token is valid or was refreshed, False if the token was not refreshed or is invalid
        """
        current_time = time.time()
        required_remaining_time = 20  # seconds
        token_remaining_time = (
            self._token_exp - current_time if self._token_exp != None else None
        )
        logging.getLogger(__name__).debug(
            f"remaining token time {token_remaining_time if token_remaining_time is not None else 0:.1f}"
        )
        if self._token_response:
            if token_remaining_time > self._token_required_remaining_time:
                logging.getLogger(__name__).debug("token still valid")
                return True
            elif self._token_response.get("refresh_token", None) != None:
                logging.getLogger(__name__).debug("refreshing token")

                r_refresh = requests.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "grant_type": "refresh_token",
                        "refresh_token": self._token_response["refresh_token"],
                    },
                )
                if "access_token" in r_refresh.json():
                    logging.getLogger(__name__).debug("refreshing token refreshed")
                    self._token_response = r_refresh.json()
                    #the refresh token is for the original client id, we are refreshing we need to token exchange again
                    aud = parse_token(self._token_response["access_token"])["aud"]
                    if self.target_client_id is not None and aud != self.target_client_id:
                        self._token_response = token_exchange(
                            client_id=self.client_id,
                            client_secret=self.client_secret,
                            target_client_id=self.target_client_id,
                            token=self._token_response["access_token"],
                            token_url=self.token_url,
                        ) 

                    self._post_update_token()
                    return True

        self._token_response = None
        return False

    def _set_token(self):
        """
        if no token or token is expired, it obtains and sets the access token
        """
        if self._token_response == None and self.use_auth_file:
            self._token_response = self._read_auth_from_file()
            self._post_update_token(validate_token=False, write_to_file=False)

        if not self._refresh_token():
            self._set_token_impl()
            self._post_update_token()

    def _post_update_token(self, validate_token=True, write_to_file=True):
        """
        does any required post processing after the token has been updated
        currently sets the _token_iat,_token_exp, writes to file eetc
        :param validate_token: validate the claims of the token, normally true but if you want to get
                               if its expired for example, would be False
        :param write_to_file: whether to write the token to file or not, also requires use_auth_file to be true
        """
        if self._token_response == None:
            self._token_exp = None
            self._token_iat = None
        else:
            claims = parse_token(
                self._token_response["access_token"], validate=validate_token
            )
            self._token_iat = claims["iat"]
            self._token_exp = claims["exp"]
            if self.use_auth_file and write_to_file:
                self._write_auth_to_file()

    def _get_auth_filename(self):
        """
        specifies the name of the file to store the auth session in
        """
        token_filename_tag = ""
        if self.target_client_id:
            token_filename_tag = f"_{self.client_id}_{self.target_client_id}"
        elif self.client_id:
            token_filename_tag = f"_{self.client_id}"

        return f"access_token{token_filename_tag}.json"

    @abc.abstractmethod
    def _set_token_impl(self):
        """
        derived classes should define this method to set the token_ member to the requested token
        it is assumed the _refresh_token check is already done
        """
        pass

    def headers(self, extra_headers=None):
        """
        returns the necessary headers to pass the token to the api call
        this only addes the Authorization header if there exists a token, cookies are handled by cookies()
        :param extra_headers: any extra headers to add to the request, this is a dictionary which is then updated with the Authorization key
        """
        new_headers = dict(extra_headers) if extra_headers != None else {}
        if self.token() != None:
            new_headers.update({"Authorization": "Bearer " + self.token()})

        return new_headers

    def token(self):
        """
        returns the access token, throws an AuthError if unable to do so
        """
        self._set_token()
        return self._token_response["access_token"]

    def authparams(self, headers=None):
        """
        returns the auth parameters, this is a dictionary which can be passed to the requests library, for token auth, this is just the headers
        """
        return {"headers": self.headers(headers)}

    def _get_auth_json_repr(self):
        """
        returns the json representation of the token response (which is already in this format...)
        """
        return self._token_response


class ClientAuth(TokenAuthBase):
    """
    oidc token retriver which takes a client_id, secret and requests a token for a given application (audience)

    """

    def __init__(
        self,
        client_id,
        client_secret,
        target_client_id=None,
        audience=None,
        hostname="auth.cern.ch",
        realm="cern",
        use_auth_file=False,
        cert_verify=True,
    ):
        """
        :param client_id: id of the client to authenticate as
        :param client_secret: secret of the client to authenticate as
        :param audience: audience of the token, ie the client id of the target api, currently being phased out in favor of target_client_id for homogenity
        :param target_client_id: audience of the token, ie the client id of the target api, replacement for audience, is an error specify both        
        :param hostname: the hostname of the authentication service (default: auth.cern.ch)
        :param realm: the realm of the authentication service (default: cern)
        :param use_auth_file: whether to save the auth credentials to file for reuse
        :param cert_verify: verify the certificate of the api_access_token_url
        """
        if audience and target_client_id:
            raise ValueError(
                "cannot specify both audience and target_client_id for ClientAuth, please use just target_client_id"
            )
        if audience:
            print("audience is deprecated, please use target_client_id instead")
            target_client_id = audience

        super().__init__(
            client_id=client_id,
            target_client_id=target_client_id,
            hostname=hostname,
            realm=realm,
            use_auth_file=use_auth_file,
        )
        self.client_secret = client_secret
        self.cert_verify = cert_verify

    def _set_token_impl(self):
        """
        requests and saves a token from the issuer (eg the CERN SSO service)
        throws an exception AuthError if it was not successful

        :raises AuthError: incase of unsuccessful authentication
        """

        token_req_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": self.target_client_id,
        }
        rep = requests.post(
            self.api_access_token_url, data=token_req_data, verify=self.cert_verify
        )
        if rep.status_code != 200 or not "access_token" in rep.json():
            raise AuthError(rep.content.decode())

        self._token_response = rep.json()


class AuthGetSSOTokenAuth(TokenAuthBase):
    """
    oidc token retriver which logs in via kerberos using auth-get-sso-token
    mostly for folks who want to be "official"(ish)

    As of Jan15th, 2025, CERN upgraded to keycloak which broke auth-get-sso-token. Thus this class has been removed
    """

    def __init__(
        self,*args,**kwargs,
    ):
        raise RuntimeError(
            "auth-get-sso-token was broken by the upgrade to KeyCloak24 on 15-01-25 and thus this class has been removed\n"
            "Please use KerbAuth or DeviceAuth instead"
        )
    def _set_token_impl():
        pass

class KerbAuth(TokenAuthBase):
    """
    oidc token retriver which logs in via kerberos

    """

    def __init__(
        self,
        client_id,
        client_secret=None,
        redirect_uri="http://localhost:8080/",
        target_client_id=None,
        hostname="auth.cern.ch",
        realm="cern",
        use_auth_file=True,
        cert_verify=True,
        redirect_url=None,
    ):
        """
        :param client_id: id of the client to authenticate as
        :param client_secret: secret of the client to authenticate as (None if a public client)
        :param redirect_uri: a valid redirect_uri of the above client
        :param target_client_id: the client_id of the application you wish to exchange your token for (None means no token exchange is required)
        :param hostname: the hostname of the authentication service (default: auth.cern.ch)
        :param realm: the realm of the authentication service (default: cern)
        :param use_auth_file: whether to save the auth credentials to file for reuse
        :param cert_verify: verify the certificate of the token exchange url
        :param redirect_url: deprecated, please use redirect_uri instead (overrides redirect_uri)
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            target_client_id=target_client_id,
            hostname=hostname,
            realm=realm,
            use_auth_file=use_auth_file,
        )
        if redirect_url is not None:
            print(
                "KerbAuth: redirect_url is deprecated, please use redirect_uri instead\n",
                "redirect_url will be removed in a future version",
                "currently redirect_url overrides redirect_uri",
            )

        self.redirect_uri = redirect_uri if redirect_url is None else redirect_url
        self.cert_verify = cert_verify

    def _set_token_impl(self):
        """
        requests and saves a token from the issuer (eg the CERN SSO service)
        throws an exception AuthError if it was not successful

        code is heavily borrowed from https://gitlab.cern.ch/authzsvc/tools/auth-get-sso-cookie/
        """

        random_state = str(uuid.uuid4()).split("-")[0]
        auth_url = f"{self.auth_url}?client_id={self.client_id}&response_type=code&state={random_state}&redirect_uri={self.redirect_uri}"
        session, r_token = KerbLogin.login(auth_url, self.hostname, self.realm)
        # so we might get a access token or we might have got a code to get an access token
        if r_token.text == "":
            r_token_redirect_params = urllib.parse.parse_qs(
                urllib.parse.urlparse(r_token.headers["Location"]).query
            )
            if "code" not in r_token_redirect_params:
                raise AuthError(
                    f"Login failed, no token in body, no code in redirect url"
                )
            else:
                r_token = session.post(
                    self.token_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "authorization_code",
                        "code": r_token_redirect_params["code"],
                        "redirect_uri": self.redirect_uri,
                    },
                    verify=self.cert_verify,
                )

        if "access_token" in r_token.json():
            token = r_token.json()

        else:
            raise AuthError(
                f"""The following error occured when getting the token                            
                            {r_token.text}                                                        
                            """
            )

        # see if we need to token swap, if not, we are done
        if not self.target_client_id:
            self._token_response = token
            return

        self._token_response = token_exchange(
            client_id=self.client_id,
            client_secret = self.client_secret,
            target_client_id=self.target_client_id,
            token=token["access_token"],
            token_url=self.token_url,
        )


class DeviceAuth(TokenAuthBase):
    """
    gets a token via device authorization flow

    """

    def __init__(
        self,
        client_id,
        client_secret=None,
        target_client_id=None,
        hostname="auth.cern.ch",
        realm="cern",
        use_auth_file=True,
        cert_verify=True,
    ):
        """
        :param client_id: id of the client to authenticate as
        :param client_secret: secret of the client to authenticate as (None if a public client)
        :param client_secret: secret of the client to authenticate as (None if a public client)
        :param redirect_uri: a valid redirect_uri of the above client
        :param client_secret: secret of the client to authenticate as (None if a public client)        
        :param redirect_uri: a valid redirect_uri of the above client
        :param target_client_id: the client_id of the application you wish to exchange your token for (None means no token exchange is required)
        :param hostname: the hostname of the authentication service (default: auth.cern.ch)
        :param realm: the realm of the authentication service (default: cern)
        :param use_auth_file: whether to save the auth credentials to file for reuse
        :param cert_verify: verify the certificate of the token exchange url
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            target_client_id=target_client_id,
            hostname=hostname,
            realm=realm,
            use_auth_file=use_auth_file,
        )
        self.cert_verify = cert_verify

    def _set_token_impl(self):
        """
        sets the token via the device authorization flow
        """
        random_state = str(uuid.uuid4()).split("-")[0]
        code_verifier = generate_token(48)
        code_challenge = create_s256_code_challenge(code_verifier)

        r_token_request = requests.post(
            self.device_auth_url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "state": random_state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            },
            verify=self.cert_verify,
        )

        if r_token_request.status_code != 200:
            raise AuthError(f"Login failed, error msg {r_token_request.text}")

        print("Please visit the following url to authenticate:")
        print(r_token_request.json()["verification_uri_complete"])

        got_token = False
        start_time = time.time()
        while not got_token and time.time() - start_time < 300:
            time.sleep(5)
            r_token = requests.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": r_token_request.json()["device_code"],
                    "code_verifier": code_verifier,
                },
                verify=self.cert_verify,
            )
            if r_token.status_code == 200:
                got_token = True
        if not got_token:
            raise AuthError(
                f"Login failed timed out after 5mins, last message:\n{r_token.text}"
            )
        if "access_token" in r_token.json():
            self._token_response = r_token.json()
        else:
            raise AuthError(f"Login failed, error msg {r_token.text}")

        # see if we need to token swap, if not, we are done
        if not self.target_client_id:
            return

        self._token_response = token_exchange(
            client_id=self.client_id,
            client_secret=self.client_secret,
            target_client_id=self.target_client_id,
            token=self._token_response["access_token"],
            token_url=self.token_url,
        )


class KerbSessionAuth(SessionAuthBase):
    def __init__(self, url=None, hostname="auth.cern.ch", realm="cern",use_auth_file=False):
        """
        :params url: the url of a sso protected website to trigger the authentication request"
        :param hostname: the hostname of the authentication service (default: auth.cern.ch)
        :param realm: the realm of the authentication service (default: cern)
        :param use_auth_file: if true, the auth information is stored in a file and reused if possible
        """
        super().__init__(hostname=hostname, realm=realm, use_auth_file=use_auth_file)
        self._initial_url = url

    def _set_authsession_impl(self):
        self._authsession, r_login = KerbLogin.login(
            self._initial_url, authhostname=self.hostname, authrealm=self.realm
        )

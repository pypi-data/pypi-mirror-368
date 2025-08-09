import requests
import argparse
import tsgauth.oidcauth as oidcauth
from tsgauth.oidcauth import parse_token
import os
import sys

def get_var(args_var,args_name,env_name):
    if args_var:
        return args_var
    else:
        try:
            return os.environ[env_name]
        except KeyError:            
            print(f"Error, {args_name} not specified nor is {env_name} set, exiting")
            sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='tests a secure api')
    parser.add_argument("url",help="url")    
    parser.add_argument("--client-id",default=None,help="client id, if not specified tries from TSGAUTH_CLIENT_ID env")
    parser.add_argument("--client-secret",default=None,help="client secret, if not specified tries from TSGAUTH_CLIENT_SECRET env")
    parser.add_argument("--target-client-id",default=None)    
    
    args = parser.parse_args()  

    client_id = get_var(args.client_id,"--client-id","TSGAUTH_CLIENT_ID")
    client_secret = get_var(args.client_id,"--client-secret","TSGAUTH_CLIENT_SECRET")
        
    auth = oidcauth.ClientAuth(client_id,client_secret,args.target_client_id)
    token_claims = parse_token(auth.token(),client_id=args.target_client_id)

    r = requests.get(f"{args.url}",headers=auth.headers())

    print(r.text)
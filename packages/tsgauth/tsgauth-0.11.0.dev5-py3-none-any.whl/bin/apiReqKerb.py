import requests
import argparse
import tsgauth.oidcauth as oidcauth

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='tests a secure api')
    parser.add_argument("url",help="url")    
    parser.add_argument("--client-id",dest="client_id",default="cms-tsg-frontend-client")    
    parser.add_argument("--redirect-url",dest="redirect_uri",default="http://localhost:8080")    
    parser.add_argument("--target-client-id",dest="target_client_id",default=None)
    parser.add_argument("--cert-url",dest="cert_url",default="https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/certs")

    args = parser.parse_args()  
    auth = oidcauth.KerbAuth(args.client_id,args.redirect_uri,args.target_client_id)

    r = requests.get(f"{args.url}",headers=auth.headers())
            
    print(r.text)


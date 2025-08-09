#!/usr/bin/env python3

import tsgauth
import requests
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='downloads the raw text from a twiki page')
    parser.add_argument("--twiki",required=True,help='twiki topic')
    parser.add_argument('--output',required=True,help='file to download text to')
    
    args = parser.parse_args()
    auth = tsgauth.oidcauth.KerbSessionAuth()

    ssosession = requests.Session()

    view_url=f"https://twiki.cern.ch/twiki/bin/view/CMS/{args.twiki}?raw=text"

    
    try:
        data = ssosession.get(view_url,**auth.authparams())
        if data.text.find(f"The topic '{args.twiki}' you are trying to access does not exist, yet.</em>")!=-1:            
            print(f"twiki {args.twiki} does not exist, perhaps you mispelt it")
            raise SystemExit
        with open(args.output, 'w', encoding='ascii', errors='replace') as f:
            f.write(data.text)
        

    except requests.exceptions.ReadTimeout:
        print(f"could not read twiki {args.twiki} please check if it exists, if it does exist, twiki may be down.\n")

    
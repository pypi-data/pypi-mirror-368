#!/usr/bin/env python3

import tsgauth
import requests
import argparse
import io

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='uploads file to twiki, note it doesnt have the most robust error checking...')
    parser.add_argument("--twiki",required=True,help='twiki topic')
    parser.add_argument('--input',required=True,help='file with txt to upload')
    parser.add_argument('--force',action='store_true',help='ignores the read timeout, will mean a new twiki will be created if it does not already exist')
    parser.add_argument('--create',action='store_true',help='if the twiki doesnt exist, it creates it')
    args = parser.parse_args()
    auth = tsgauth.oidcauth.KerbSessionAuth()

    ssosession = requests.Session()

    base_view_url="https://twiki.cern.ch/twiki/bin/view/CMS/"
    base_save_url=u"https://twiki.cern.ch/twiki/bin/save/CMS/"
    
    try:
        data = ssosession.get(base_view_url+args.twiki,**auth.authparams())
        if data.text.find(f"The topic '{args.twiki}' you are trying to access does not exist, yet.</em>")!=-1:
            if args.create:
                print(f"twiki {args.twiki} does not exist, creating it")
            else:    
                print(f"twiki {args.twiki} does not exist, use --create option to create it")
                raise SystemExit

    except requests.exceptions.ReadTimeout:
        print(f"could not read twiki {args.twiki} please check if it exists, if it does exist, twiki may be down.\n If you continue to get this message use --force")
        if not args.force:
            raise SystemExit

    with io.open(args.input,mode="r",encoding="utf-8") as f:
        text = f.read()
        #okay for some reason twiki was expecting "iso-8859-1" rather than uft-8 and 
        #it seemed easier just to give it what it wants
        #the ssosession now has the twiki cookies created by reading the view twiki so the auth parameters are no longer needed
        r = ssosession.post(base_save_url+args.twiki,data={"text" : text.encode('iso-8859-1','replace')},allow_redirects=False)

#!/usr/bin/python3
"""
A Python program for sending SMS messages using the Twilio and LDS Church's LCR API's
"""

import re
import os
import sys
import logging
import argparse

from lcr import API as LCR
from twilio.rest import Client
# Download the helper library from https://www.twilio.com/docs/python/install

def confirm():
    """
    Ask user to enter Y or N (case-insensitive).
    :return: True if the answer is Y.
    :rtype: bool
    """
    answer = ""
    while answer not in ["y", "n"]:
        answer = input("\nAre you sure you want to send the SMS message(s)? [Y/n] ").lower()

    if answer == "n":
        exit("Exiting.")
    return True

def main(args):
    """
    This script is meant to be run from the cli
    """
    dnc = 'do_not_contact.txt'
    config_file = '.creds'
    do_not_contact = []
    phone_list = []

    cli = argparse.ArgumentParser(description="Send an SMS text using the Twilio API")
    cli.add_argument('-o', '--org', help="The organization you want to message. \
            This can be 'eq'for the Elders Quorum\
            'rs' for the Relief Society\
            or 'all' for everyone in the ward.")
    cli.add_argument('-b', '--body', help="The body of the message you want to send in quotes. \
            Max 160 characters.")
    cli.add_argument('-v', '--verbose', action="store_true", help="Print more verbose output.")
    opts = cli.parse_args(args)

    if len(sys.argv) == 1:
        cli.print_help()
        exit()

    if len(opts.body) > 160:
        print(f"\nYour message is {len(opts.body)} characters, the max is 160, please fix.\
                \nExiting.")
        exit(2)

    if os.path.isfile(dnc):
        with open(dnc) as do_not:
            for line in do_not:
                line = line.split('#', 1)[0]
                line = re.sub('[-().+ ]', '', line)
                if line:
                    if line.startswith("1"):  # If phone number starts with 1, remove it
                        line = line[1:]
                    do_not_contact.append(line.strip())
    
    if not os.path.exists(config_file):
        print(f'{config_file} file not found!  Exiting.')
        exit(2)

    # Get twilio account and auth info from config file
    with open(config_file) as read_file:
        lines = read_file.read().strip().split('\n')

    for line in lines:
        if 'account_sid' in line:
            pieces = line.split('=')
            account_sid = pieces[1]
        if 'auth_token' in line:
            pieces = line.split('=')
            auth_token = pieces[1]
        if 'twilio_num' in line:
            pieces = line.split('=')
            twilio_num = pieces[1]
        if 'username' in line:
            pieces = line.split('=')
            username = pieces[1]
        if 'password' in line:
            pieces = line.split('=')
            password = pieces[1]
        if 'ward_unit' in line:
            pieces = line.split('=')
            ward_unit = pieces[1]
        if 'country_code' in line:
            pieces = line.split('=')
            country_code = pieces[1]

    try:
        for config_setting in [account_sid, auth_token, twilio_num, username, password, ward_unit, country_code]:
            config_setting
    except UnboundLocalError:
        print(f'A config setting is not set in the {config_file} file.\nPlease check that you have a setting for:\n\
        account_sid, auth_token, twilio_num, username, password, ward_unit, and country_code.')
        exit(2)

    lcr = LCR(username, password, ward_unit)

    count = 0
    months = 1
    members_alt = lcr.members_alt()
    print('len members_alt', len(members_alt))
    #print(members_alt)
    for member in members_alt:
        if opts.org == 'eq':
            if member['priesthoodOffice'] != 'NONE':
                #print(member)
                print(member['nameFormats'].get('listPreferredLocal'), member['nameFormats'].get('givenPreferredLocal'), member['priesthoodOffice'], member['phoneNumber'])
                #print('---------------------------------------')
                count += 1
                #if count == 6:
                #    exit()

        elif opts.org == 'rs':
            pass
        elif opts.org == 'all':
            pass
        else
            print('Unrecognized organization!  Exiting.')
            exit(2)
    
    print('count', count)
    exit()

    client = Client(account_sid, auth_token)
    #phone_list = list(filter(None, phone_list))

    logging.basicConfig(filename='lcr-sms.log', filemode='a',\
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\
            datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

    if opts.verbose:
        print('\nMessage:')
        print(opts.body)
        print('\nPhone List:')
        print(phone_list)

    confirm() # prompt for execution
    print('')

    for phone_num in phone_list:
        phone_num = re.sub('[-().+ ]', '', phone_num)
        if phone_num.startswith("1"): # If phone_num starts with 1 remove it
            phone_num = phone_num[1:]
        if phone_num not in do_not_contact:
            message = client.messages \
                .create(
                    body=opts.body,
                    from_='+'+country_code+twilio_num, # Your twilio number. Costs about $1/month, $0.0075/SMS
                    to='+'+country_code+phone_num      # +1 is the USA country code, adjust for your location
                )
            
            output = f"phone_num = {phone_num} ; body = \"{opts.body}\" ; {message.sid}"
            logging.info(output)
            if opts.verbose:
                print(output)
    
            #exit()

    print("Done.")

if __name__ == '__main__':
    main(sys.argv[1:])


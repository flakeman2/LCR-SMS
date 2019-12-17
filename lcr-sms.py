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
    config_file = '.creds'
    account_sid = ''
    auth_token = ''
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

    if os.path.isfile(opts.list):
        with open(opts.list) as phone_file:
            for line in phone_file:
                line = line.split('#', 1)[0]
                line = re.sub('[-().+]', '', line)
                if line:
                    phone_list.append(line.strip())
    # this could be either one phone number or a bad path/file.
    #elif len(re.sub('[-().+]', '', opts.list)) < 10:
    elif opts.list.isnumeric():
        line = re.sub('[-().+]', '', opts.list)
        phone_list = line.split(' ')
    else:
        print("\nFile not found. Exiting.\n")
        exit(2)

    phone_list = list(filter(None, phone_list))

    if not os.path.exists(config_file):
        print(f'{config_file} file not found! Exiting.')
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

    client = Client(account_sid, auth_token)

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
        phone_num = phone_num.replace(" ", "")
        if phone_num.startswith("1"): # If phone_num starts with 1 remove it
            phone_num = phone_num[1:]
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


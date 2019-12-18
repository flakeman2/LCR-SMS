##########
LCR-SMS
##########

A Python program for sending SMS messages using twilio and LDS LCR API's.

Getting Started
---------------
You'll need a twilio account and access to the LDS LCR tool in order to use this program.

For twilio, sign up here:  https://www.twilio.com  
Once you have an account with a phone number, grab your 'ACCOUNT SID' and 'AUTH TOKEN'.
You can find them here:  https://twilio.com/console 
Create a credentials file, '.creds', in the base of your cloned repo with the following format::

    account_sid=##########
    auth_token=###########
    twilio_num=###########
    country_code=1       # 1 is the USA country code, adjust for your location 

For the LDS Leader and Clerk Resources (LCR tool), you'll need a calling that gives you access to membership information.
Log into https://lcr.churchofjesuschrist.org/ and find your ward unit number.
Mine was in the upper right hand corner, just under the tool bar and looked like this::

    Redacted Stake (46##90) Redacted 9th Ward (10###69)

Add your username, password, and ward unit number to the '.creds' file::

    username=########
    password=########
    ward_unit=#######

*note, this program only works for members who have a phone number listed on their LDS profile.*
*You should encourage members to update their information.*

Important
---------
Some members may not want to be contacted.  Simply create a file 'do_not_contact.txt'.
Add their phone number with any relevant information::

    123-456-7890  # Name  # NO LONGER IN WARD
    987-654-3210  # Name  # DO NOT CALL

The lcr-sms.py script will not message any numbers listed in 'do_not_contact.txt'.
   
Usage::

    lcr-sms.py [-h] [-o ORGANIZATION] [-b BODY] [-v]
    
    arguments:
      -h, --help            show this help message and exit
      -o ORGANIZATION, --org ORGANIZATION  The group you want to message.
                            This can be 'eq'for the Elders Quorum
                            'rs' for the Relief Society
                            or 'all' for everyone in the ward.
      -b BODY, --body BODY  The body of the message you want to send in quotes.
                            Max 160 characters.
      -v, --verbose         Print more verbose output.

Examples::

    lcr-sms.py -o eq -b "Saturday at 9:30am.  Please come"
    lcr-sms.py -o rs -b "The Party is on!" -v


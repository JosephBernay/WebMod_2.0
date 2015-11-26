# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import json
import urllib2


def get_emails(url):
    """This Python function is not a controller.  A function defines a controller in web2py
    iff it does not take any arguments.  This function takes arguments, and so it's a normal
    function you can call from your controllers."""
    try:
        r = urllib2.urlopen(url)
        email_list = json.load(r)
        r.close()
    except Exception, e:
        email_list = []
        session.message = T('Error in contacting server')
    return email_list


def index():
    """
    Displays list of all emails.
    """
    # Gets some fresh set of emails each time.
    email_list = get_emails('http://luca-teaching.appspot.com/fake_emails/default/get_emails')
    # We store the list of emails in the session.
    session.email_list = email_list
    # At this point, email_list is a list of dictionaries of this format:
    #     {
    #         'id': 'randomstringid',
    #         'from': 'sender@email.com',
    #         'date': 'somedateinISOformat',
    #         'subject': 'Your homework.',
    #         'text': 'Text of email, with \n\n used to separate paragraphs',
    #         'starred': True, # or False!
    #         'read': False, # Whether you have read it or not, can be True or False
    #     }
    # And you need to display the list of emails.
    return dict(email_list=email_list)


def read_email():
    """This controller is in charge of displaying an individual email.
    You can access it via the url URL('default', 'read_email', args=[email_id])
    for the appropriate email_id."""
    # First, we ensure we have the list of emails.
    email_list = session.email_list
    if email_list is None:
        # This should not happen, but just in case.
        email_list = get_emails('http://luca-teaching.appspot.com/fake_emails/default/get_emails')
        session.email_list = email_list
    # Makes a dictionary of the email list, so given the ID we can find the email.
    # This is a bit overkill, we could just traverse the list to find it, but
    # so you can have a bit of fun seeing some Python code.
    email_dict = {e['id']: e for e in email_list}
    # Figures out which email we wish.
    email_id = request.args(0)
    if email_id is None or email_id not in email_dict:
        session.message = T('No such message')
        redirect(URL('default', 'index'))
    email = email_dict[email_id]
    # Ok, great, now we have the email to display.
    return dict(email=email)



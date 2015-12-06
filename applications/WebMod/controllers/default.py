# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import json
import urllib2
from datetime import datetime

def index():
    """
    Displays list of all emails.
    """
    '''# Gets some fresh set of emails each time.
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
    # And you need to display the list of emails.'''
    email_list = []
    return dict(email_list=email_list)

@auth.requires_login()
def modeling():
    active_model_id = ""

    return dict(active_model_id=active_model_id)

def save_model():
    db.model.update_or_insert((db.model.model_id == request.vars.model_id),
        name=request.vars.name,
        description=request.vars.description,
        tag_list=json.loads(request.vars.tag_list),
        mesh_list=json.loads(request.vars.mesh_list),
        thumbnail_image=request.vars.thumbnail_image,
        last_edited=datetime.utcnow(),
        model_id=request.vars.model_id)

    print request.vars.mesh_list

    model = db(db.model.model_id == request.vars.model_id).select()
    print model

    return "ok"

def load_model():
    model = db((db.model.name == request.vars.name) & (db.model.user_id == auth.user_id)).select()

    print model

def resetDB():
    db(db.model.id > 0).delete()

def profile():
    data = []
    return dict(data=data)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires usership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_usership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    form = auth()
    print('\n \n')
    #print(form.element(_type='submit')['value'])
 
    return dict(form=form)



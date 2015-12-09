# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import json
import urllib2
from datetime import datetime
from gluon import utils as gluon_utils

def index():
    models = db().select(db.model.ALL, orderby=~db.model.num_favorites)
    return dict(models=models, x=0)

@auth.requires_login()
def modeling():
    active_model_id = ""
    active_model_name = "Untitled"
    if len(request.args) == 1:
        active_model_id = request.args(0)
        m_list = db(db.model.model_id == active_model_id).select()
        if len(m_list) != 0:
            m = m_list.__getitem__(0)
            if m.user_id != auth.user_id:
                response.flash=T("You cannot open this model.")
                active_model_id = ""
                active_model_name = "Untitled"
            else:
                active_model_name = m.name
        else:
            response.flash=T("This model does not exist.")

    return dict(active_model_id=active_model_id, active_model_name=active_model_name)

def viewing():
    model_id = request.args(0)

    print model_id

    return dict(model_id=model_id)

def view_model():
    m_list = db(db.model.model_id == request.vars.model_id).select()
    m = m_list.__getitem__(0)
    model = {'name': m.name,
             'description': m.description,
             'tag_list': m.tag_list,
             'mesh_list': m.mesh_list,
             'model_id': m.model_id}
    return response.json(dict(model=model))

def copy_model():
    model_id = request.vars.model_id
    m_list = db(db.model.model_id == request.vars.model_id).select()
    m = m_list.__getitem__(0)

    db.model.insert(name=request.vars.name,
                    description=request.vars.description,
                    tag_list=json.loads(request.vars.tag_list),
                    mesh_list=json.loads(request.vars.mesh_list),
                    thumbnail_image=request.vars.thumbnail_image,
                    last_edited=datetime.utcnow(),
                    model_id=gluon_utils.web2py_uuid())

    response.flash=T(m.user_id + "'s model " + '"m.name" has been saved to your profile.')


def save_model():
    print request.vars.model_id
    db.model.update_or_insert((db.model.model_id == request.vars.model_id),
        name=request.vars.name,
        description=request.vars.description,
        tag_list=json.loads(request.vars.tag_list),
        mesh_list=json.loads(request.vars.mesh_list),
        thumbnail_image=request.vars.thumbnail_image,
        isPublic=request.vars.isPublic,
        isShareable=request.vars.isShareable,
        last_edited=datetime.utcnow(),
        model_id=request.vars.model_id)

    # print request.vars.mesh_list
    #
    # model = db(db.model.model_id == request.vars.model_id).select()
    # print model

    return "ok"

def open_model():
    m_list = db((db.model.name == request.vars.name) & (db.model.user_id == auth.user_id)).select()
    model = {'exists': "No"}
    if len(m_list) != 0:
        m = m_list.__getitem__(0)
        model = {'exists': "Yes",
                 'name': m.name,
                 'description': m.description,
                 'tag_list': m.tag_list,
                 'mesh_list': m.mesh_list,
                 'isPublic': m.isPublic,
                 'isShareable': m.isShareable,
                 'model_id': m.model_id}
    else:
        response.flash=T('You have no model named "' + request.vars.name + '"');
    return response.json(dict(model=model))

def search():
    models = db(db.model).select(db.model.ALL)
    userid = 0
    if auth.user_id:
        userid=auth.user_id
    return dict(models=models, userid=userid)

def search_stuff():
    search_text = request.vars.content
    search_type = request.vars.search_type
    if search_type == "name":
        models = db(db.model.name == search_text).select()
        first = models.first()
        if not first:
            response.flash = T("No  model by that name")
            return response.json(dict(model={}))
    elif search_type == "user_id":
        username = db(db.auth_user.username == search_text).select()
        if username.first():
            models = db(db.model.user_id == username.first().id).select()
            first = models.first()
            if not first:
                response.flash = T("User has no models")
                return response.json(dict(model={}))
        else:
            response.flash = T("No user by that name")
            return response.json(dict(model={}))
    elif search_type == "tag_list":
        stuff = db(db.model).select()
        models = []
        for m in stuff:
            if search_text in m.tag_list['tags']:
                models.append(m)
        first = len(models)
        if not first:
            response.flash = T("No model with that tag")
            return response.json(dict(model={}))
    if auth.user_id:
        model = {m.name: {'thumbnail': m.thumbnail_image,
                        'public': m.isPublic,
                            'share': m.isShareable,
                            'favorites': m.num_favorites,
                            'model_id': m.model_id,
                            'favorited': m.model_id in db.auth_user(auth.user_id)['favorited_models'].split()}
                            for m in models}
    else:
        model = {m.name: {'thumbnail': m.thumbnail_image,
                        'public': m.isPublic,
                            'share': m.isShareable,
                            'favorites': m.num_favorites,
                            'model_id': m.model_id,
                            'favorited': False}
                            for m in models}
    return response.json(dict(model=model))

def resetDB():
   db(db.model.id > 0).delete()
    
def download():
    return response.download(request, db)

def profile():
   if (auth.user_id == None):
      redirect(URL('default', 'user', args=['login']))
   if request.args(0) == None:
      redirect(URL('default', 'profile', args=[auth.user_id]))   
   user = db.auth_user(request.args(0))                                   
   return dict(user=user)
   
def load_fav_models():
   id = request.vars.profile_id
   user = db.auth_user(auth.user_id)['favorited_models']
   models = db().select(db.model.ALL)
   model_fav_list = {}
   index = 0
   if int(id) != int(auth.user_id):
      for m in models:
         if ((int(m.user_id) == int(id)) and (index < 3) and (m.isPublic == True)):
            fav = False;
            if((user.find((" "+m.model_id+" "))) != -1):
               fav = True;
            model_fav_list[m.id] = {'name': m.name,
                                       'description': m.description,
                                       'tag_list': m.tag_list,
                                       'mesh_list': m.mesh_list,
                                       'thumbnail_image': m.thumbnail_image,
                                       'isPublic': m.isPublic,
                                       'isShareable': m.isShareable,
                                       'num_favorites': m.num_favorites,
                                       'last_edited': m.last_edited,
                                       'user_id': m.user_id,
                                       'username': db.auth_user(m.user_id)['username'],
                                       'model_id': m.model_id,
                                       'favorited': fav} 
         index = index + 1
   else: 
      for m in models:
         if ((int(m.user_id) == int(id)) and (index < 3)):
            fav = False;
            if((user.find((" "+m.model_id+" "))) != -1):
               fav = True;
            model_fav_list[m.id] = {'name': m.name,
                                       'description': m.description,
                                       'tag_list': m.tag_list,
                                       'mesh_list': m.mesh_list,
                                       'thumbnail_image': m.thumbnail_image,
                                       'isPublic': m.isPublic,
                                       'isShareable': m.isShareable,
                                       'num_favorites': m.num_favorites,
                                       'last_edited': m.last_edited,
                                       'user_id': m.user_id,
                                       'username': db.auth_user(m.user_id)['username'],
                                       'model_id': m.model_id,
                                       'favorited': fav}
         index = index + 1
   limit = 0
   sorted_models = []
   for s in sorted(model_fav_list.iteritems(), key=lambda (x, y): y['num_favorites'], reverse=True):
      if limit < 3:
         sorted_models.append(s[1])
      limit = limit + 1
   return response.json(dict(model_fav_dict = sorted_models))
   
def load_models():
   id = request.vars.profile_id
   row = int(request.vars.row)
   user = db.auth_user(auth.user_id)['favorited_models']
   models = db().select(db.model.ALL, orderby=db.model.name)
   model_list = {}
   index = 0
   if int(id) != int(auth.user_id):
      for m in models:
         if ((index >= (row * 5)) and (index < ((row*5)+5)) and (m.isPublic == True)):
            if ((int(m.user_id) == int(id))):
               fav = False;
               if((user.find((" "+m.model_id+" "))) != -1):
                  fav = True;
               model_list[m.id] = {'name': m.name,
                                          'description': m.description,
                                          'tag_list': m.tag_list,
                                          'mesh_list': m.mesh_list,
                                          'thumbnail_image': m.thumbnail_image,
                                          'isPublic': m.isPublic,
                                          'isShareable': m.isShareable,
                                          'num_favorites': m.num_favorites,
                                          'last_edited': m.last_edited,
                                          'user_id': m.user_id,
                                          'username': db.auth_user(m.user_id)['username'],
                                          'model_id': m.model_id,
                                          'favorited': fav} 
         index = index + 1
   else:
      for m in models:
         if ((index >= (row * 5)) and (index < ((row*5)+5))):
            if ((int(m.user_id) == int(id))):
               fav = False;
               if((user.find((" "+m.model_id+" "))) != -1):
                  fav = True;
               model_list[m.id] = {'name': m.name,
                                          'description': m.description,
                                          'tag_list': m.tag_list,
                                          'mesh_list': m.mesh_list,
                                          'thumbnail_image': m.thumbnail_image,
                                          'isPublic': m.isPublic,
                                          'isShareable': m.isShareable,
                                          'num_favorites': m.num_favorites,
                                          'last_edited': m.last_edited,
                                          'user_id': m.user_id,
                                          'username': db.auth_user(m.user_id)['username'],
                                          'model_id': m.model_id,
                                          'favorited': fav} 
         index = index + 1
   return response.json(dict(model_dict=model_list))
   
def favorite_model():
   modelID = request.vars.model_id
   model = db(db.model.model_id == modelID).select()
   num = 0
   favs = ''
   for m in model:
      num = m.num_favorites
   num = num + 1
   db.model.update_or_insert((db.model.model_id == modelID),
                                 num_favorites = num)
   user = db(db.auth_user.id == auth.user_id).select()
   for u in user:
      favs = u.favorited_models
   favs = favs + ' ' + modelID + ' '
   db.auth_user.update_or_insert((db.auth_user.id == auth.user_id),
                                 favorited_models = favs)
   return
   
def unfavorite_model():
   modelID = request.vars.model_id
   model = db(db.model.model_id == modelID).select()
   num = 0
   favs = ''
   for m in model:
      num = m.num_favorites
   num = num - 1
   db.model.update_or_insert((db.model.model_id == modelID),
                                 num_favorites = num)
   user = db(db.auth_user.id == auth.user_id).select()
   for u in user:
      favs = u.favorited_models
   favs = favs.replace((' ' + modelID + ' '), '')
   db.auth_user.update_or_insert((db.auth_user.id == auth.user_id),
                                 favorited_models = favs)
   return
   
def load_favs():
   id = request.vars.profile_id
   row = int(request.vars.row)
   user = db.auth_user(auth.user_id)['favorited_models']
   profile = db.auth_user(id)['favorited_models']
   favs = profile.split()
   favs_dict = {}
   favs_dict2 = {}
   index = 0;
   if int(id) != int(auth.user_id):
      for f in favs:
         if ((index >= (row * 5)) and (index < ((row*5)+5)) and (m.isPublic == True)):
            model = db(db.model.model_id == f).select();
            for m in model:
               fav = False;
               if((user.find((" "+m.model_id+" "))) != -1):
                  fav = True;
               favs_dict[m.id] = {'name': m.name,
                                          'description': m.description,
                                          'tag_list': m.tag_list,
                                          'mesh_list': m.mesh_list,
                                          'thumbnail_image': m.thumbnail_image,
                                          'isPublic': m.isPublic,
                                          'isShareable': m.isShareable,
                                          'num_favorites': m.num_favorites,
                                          'last_edited': m.last_edited,
                                          'user_id': m.user_id,
                                          'username': db.auth_user(m.user_id)['username'],
                                          'model_id': m.model_id,
                                          'favorited': fav} 
         elif ((index >= (row * 5+5)) and (index < ((row*5)+10)) and (m.isPublic == True)):
            model = db(db.model.model_id == f).select();
            for m in model:
               fav = False;
               if((user.find((" "+m.model_id+" "))) != -1):
                  fav = True;
               favs_dict2[m.id] = {'name': m.name,
                                          'description': m.description,
                                          'tag_list': m.tag_list,
                                          'mesh_list': m.mesh_list,
                                          'thumbnail_image': m.thumbnail_image,
                                          'isPublic': m.isPublic,
                                          'isShareable': m.isShareable,
                                          'num_favorites': m.num_favorites,
                                          'last_edited': m.last_edited,
                                          'user_id': m.user_id,
                                          'username': db.auth_user(m.user_id)['username'],
                                          'model_id': m.model_id,
                                          'favorited': fav} 
         index = index + 1
   else:
      for f in favs:
         if ((index >= (row * 5)) and (index < ((row*5)+5))):
            model = db(db.model.model_id == f).select();
            for m in model:
               fav = False;
               if((user.find((" "+m.model_id+" "))) != -1):
                  fav = True;
               favs_dict[m.id] = {'name': m.name,
                                          'description': m.description,
                                          'tag_list': m.tag_list,
                                          'mesh_list': m.mesh_list,
                                          'thumbnail_image': m.thumbnail_image,
                                          'isPublic': m.isPublic,
                                          'isShareable': m.isShareable,
                                          'num_favorites': m.num_favorites,
                                          'last_edited': m.last_edited,
                                          'user_id': m.user_id,
                                          'username': db.auth_user(m.user_id)['username'],
                                          'model_id': m.model_id,
                                          'favorited': fav} 
         elif ((index >= (row * 5+5)) and (index < ((row*5)+10))):
            model = db(db.model.model_id == f).select();
            for m in model:
               fav = False;
               if((user.find((" "+m.model_id+" "))) != -1):
                  fav = True;
               favs_dict2[m.id] = {'name': m.name,
                                          'description': m.description,
                                          'tag_list': m.tag_list,
                                          'mesh_list': m.mesh_list,
                                          'thumbnail_image': m.thumbnail_image,
                                          'isPublic': m.isPublic,
                                          'isShareable': m.isShareable,
                                          'num_favorites': m.num_favorites,
                                          'last_edited': m.last_edited,
                                          'user_id': m.user_id,
                                          'username': db.auth_user(m.user_id)['username'],
                                          'model_id': m.model_id,
                                          'favorited': fav} 
         index = index + 1
   return response.json(dict(fav_dict=favs_dict, fav_dict2=favs_dict2))

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
    
    #print(auth.user.first_name)
    #print(db.auth_user[auth.user_id].first_name)
    
    form = auth()
    return dict(form=form)



# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import json
import urllib2
from datetime import datetime

def index():
    models = db().select(db.model.ALL, orderby=db.model.num_favorites)
    return dict(models=models, x=0)

@auth.requires_login()
def modeling():
    if request.args(0) == None:
        active_model_id = ""
        active_model_name = "Username"
    else:
        active_model_id = request.args(0)
    importing = False

    return dict(active_model_id=active_model_id, active_model_name=active_model_name)

def save_model():
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
    m = db((db.model.name == request.vars.name) & (db.model.user_id == auth.user_id)).select().__getitem__(0)
    print m
    model = {'name': m.name,
            'description': m.description,
            'tag_list': m.tag_list,
            'mesh_list': m.mesh_list,
            'isPublic': m.isPublic,
            'isShareable': m.isShareable,
            'model_id': m.model_id}
    return response.json(dict(model=model))

def search():
    models = db(db.model).select(db.model.ALL)
    return dict(models=models)

def search_stuff():
   search_text = request.vars.content
   search_type = request.vars.search_type
   if search_type == "name":
      print search_text
      models = db(db.model.name == search_text).select()
   elif search_type == "user_id":
      username = db(db.auth_user.username == search_text).select()[0]
      models = db(db.model.user_id == username.id).select()
   elif search_type == "tag_list":
      stuff = db(db.model).select()
      models = []
      for m in stuff:
         if search_text in m.tag_list['tags']:
            models.append(m)
   if models:
        for m in models:
            print(m.isPublic, m.isShareable)
        model = {m.name: {'thumbnail': m.thumbnail_image,
                            'public': m.isPublic,
                            'share': m.isShareable,
                            'favorites': m.num_favorites,
                            'model_id': m.model_id}
                 for m in models}
        return response.json(dict(model=model))
   else:
      print "damn"
      response.flash = T("Hello World")
      return respone.json(dict(model={}))

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
            model_fav_list[m.num_favorites] = {'name': m.name,
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
            model_fav_list[m.num_favorites] = {'name': m.name,
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
   return response.json(dict(model_fav_dict = model_fav_list))
   
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
   user = db.auth_user(auth.user_id)['favorited_models']
   favs = user.split()
   return

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



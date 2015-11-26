# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
from datetime import datetime
from gluon import utils as gluon_utils
import json
import time

TIMES_TO_PAGINATE_BOARDS = 1
TIMES_TO_PAGINATE_POSTS = 1

def index():
    bulletin_boards = db().select(db.bulletin_boards.ALL)
    posts = db().select(db.posts.ALL)
    logger.info("Here we are, in the controller.")
    response.flash = T("Hello World")
    # return number of pages of boards to be displayed
    # num_times = request.args(0)
    # if num_times == None or int(num_times) < 1:
    #     num_times = 1
    # if num_times >= TIMES_TO_PAGINATE_BOARDS:
    #     return dict(bulletin_boards=bulletin_boards, posts=posts, times=num_times)
    # else:
    #     return dict(bulletin_boards=bulletin_boards, posts=posts, times=TIMES_TO_PAGINATE_BOARDS)
    draft_id = gluon_utils.web2py_uuid()
    d = {b.id: {'board_title': b.title,
                'board_id': b.board_id}
         for b in bulletin_boards}
    return (dict(draft_id=draft_id))

def bulletin_board():
    """This controller is in charge of displaying an individual board"""
    # First, we ensure we have the list of boards.
    bulletin_boards = db().select(db.bulletin_boards.ALL)
    # Figures out which board we desire.
    board = None
    board_id = request.args(0)
    for item in bulletin_boards:
        if int(board_id) == int(item['id']):
            board = item
            break
    # Second, we ensure we have the list of posts.
    posts = db().select(db.posts.ALL)
    #Figures out which post(s) we desire.
    post_list = []
    for item in posts.sort(lambda post: post.last_edited, reverse=True):
        if int(board_id) == item['bulletin_board']:
            post_list.append(item);
    # num_times = request.args(1)
    # if num_times == None or int(num_times) < 1:
    #     num_times = 1
    # Ok, great, now we have the posts to display.
    # if num_times >= TIMES_TO_PAGINATE_POSTS:
    #     return dict(post_list=post_list, board=board, times=num_times, draft_id=draft_id)
    # else:
    #     return dict(post_list=post_list, board=board, times=TIMES_TO_PAGINATE_POSTS, draft_id=draft_id)
    draft_id = gluon_utils.web2py_uuid()
    return dict(draft_id=draft_id, board=board, post_list=post_list)

def add_board():
    db.bulletin_boards.insert(title=request.vars.title,
                              board_id=request.vars.board_id)
    return "ok"

def add_post():
    db.posts.update_or_insert((db.posts.post_id == request.vars.post_id),
            post_id=request.vars.post_id,
            title=request.vars.post_title,
            description=request.vars.post_desc,
            user_id=request.vars.user_id,
            bulletin_board=request.vars.bulletin_board,
            is_draft=request.vars.is_draft,
            loading_post=request.vars.loading_post)
    return "ok"

def load_boards():
    boards = db().select(db.bulletin_boards.ALL)
    d = {b.board_id: {'uri': URL('default', 'bulletin_board', args=b.id),
                'title': b.title,
                'board_id': b.board_id,
                'loading_board': b.loading_board}
         for b in boards}
    return response.json(dict(board_dict=d))

def load_posts():
    posts = db(db.posts.bulletin_board == request.vars.board_id).select()
    d = {p.post_id: {'title': p.title,
                'description': p.description,
                'user_id': p.user_id,
                'is_draft': p.is_draft,
                'post_id': p.post_id,
                'marked_for_delete': p.marked_for_delete,
                'loading_post': p.loading_post}
         for p in posts}
    return response.json(dict(post_dict=d))

def mark_delete():
    db(db.posts.post_id == request.vars.post_id).update(marked_for_delete = True)
    db.delete_queue.insert(post_id=request.vars.post_id)

def unmark_delete():
    db(db.posts.post_id == request.vars.post_id).update(marked_for_delete = False)
    db(db.delete_queue.post_id == request.vars.post_id).delete()

def delete_marked():
    marked_posts = db().select(db.delete_queue.ALL)
    for post in marked_posts:
        db(db.posts.post_id == post['post_id']).delete()
    db(db.delete_queue.id > 0).delete()

# delete all boards and posts
def reset():
    db(db.bulletin_boards.id > 0).delete()
    db(db.posts.id > 0).delete()

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
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()



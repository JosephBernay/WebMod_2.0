# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
from datetime import datetime

TIMES_TO_PAGINATE_BOARDS = 1
TIMES_TO_PAGINATE_POSTS = 1

def index():
    bulletin_boards = db().select(db.bulletin_boards.ALL)
    posts = db().select(db.posts.ALL)
    logger.info("Here we are, in the controller.")
    response.flash = T("Hello World")
    # return number of pages of boards to be displayed
    num_times = request.args(0)
    if num_times == None or int(num_times) < 1:
        num_times = 1
    if num_times >= TIMES_TO_PAGINATE_BOARDS:
        return dict(bulletin_boards=bulletin_boards, posts=posts, times=num_times)
    else:
        return dict(bulletin_boards=bulletin_boards, posts=posts, times=TIMES_TO_PAGINATE_BOARDS)

def bulletin_board():
    """This controller is in charge of displaying an individual board"""
    # First, we ensure we have the list of boards.
    bulletin_boards = db().select(db.bulletin_boards.ALL)
    # Figures out which board we desire.
    board = None
    board_id = request.args(0)
    for item in bulletin_boards:
        if int(board_id) == item['id']:
            board = item
            break
    # Second, we ensure we have the list of posts.
    posts = db().select(db.posts.ALL)
    #Figures out which post(s) we desire.
    post_list = []
    for item in posts.sort(lambda post: post.last_edited, reverse=True):
        if int(board_id) == item['bulletin_board']:
            post_list.append(item);
    num_times = request.args(1)
    if num_times == None or int(num_times) < 1:
        num_times = 1
    # Ok, great, now we have the posts to display.
    if num_times >= TIMES_TO_PAGINATE_POSTS:
        return dict(post_list=post_list, board=board, times=num_times)
    else:
        return dict(post_list=post_list, board=board, times=TIMES_TO_PAGINATE_POSTS)

def add_board():
    """Lets the user add a board."""
    logger.info("My session is: %r" % session)
    form = SQLFORM(db.bulletin_boards)
    if form.process().accepted:
        session.flash = T('Your board was created')
        redirect(URL('default', 'bulletin_board', args=[form.vars.id]))
    return dict(form=form)

def add_post():
    """Lets the user add a post to a board."""
    logger.info("My session is: %r" % session)
    board_id = request.args[0]
    form = SQLFORM(db.posts)
    form.vars.bulletin_board = board_id
    if form.process().accepted:
        session.flash = T('Your post was created')
        # update the 'last_edited' field of bulletin_boards
        db(db.bulletin_boards.id == request.args(0)).update(last_edited=datetime.utcnow())
        redirect(URL('default', 'bulletin_board', args=[board_id]))
    else:
        logger.info("blargh")
    return dict(form=form)

def edit_post():
    """Lets the user edit a post on a board"""
    post_record = db.posts(request.args(0))
    form = SQLFORM(db.posts, post_record)
    if form.process().accepted:
        session.flash = T('Your post was edited')
        db(db.posts.id == request.args(0)).update(last_edited=datetime.utcnow())
        redirect(URL('default', 'bulletin_board', args=[request.args(1)]))
    return dict(form=form)

def delete_post():
    """Lets the user delete a post from a board"""
    db(db.posts.id == request.args(0)).delete()
    redirect(URL('default', 'bulletin_board', args=[request.args(1)]))

def view_single_post():
    post = db.posts(request.args(0))
    return dict(post=post)

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



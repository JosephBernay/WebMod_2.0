#########################################################################
## Define your tables below; for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

from datetime import datetime

db.define_table('bulletin_boards',
                Field('title'),
                Field('last_edited', 'datetime'),
                Field('user_id', db.auth_user),
                )

db.bulletin_boards.title.requires = [IS_NOT_EMPTY(error_message='This field is required'),
                                     IS_NOT_IN_DB(db, 'bulletin_boards.title', error_message='A board with this title already exists.')]
db.bulletin_boards.last_edited.default = datetime.utcnow()
db.bulletin_boards.last_edited.writable = False
db.bulletin_boards.last_edited.label = "Created On"
db.bulletin_boards.user_id.default = auth.user_id
db.bulletin_boards.user_id.readable = db.bulletin_boards.user_id.writable = False

db.define_table('posts',
                Field('title'),
                Field('description', 'text'),
                Field('last_edited', 'datetime'),
                Field('bulletin_board', 'reference bulletin_boards'),
                Field('user_id', db.auth_user),
                )

db.posts.title.requires = IS_NOT_EMPTY(error_message='This field is required')
db.posts.description.requires = IS_NOT_EMPTY(error_message='This field is required')
db.posts.last_edited.default = datetime.utcnow()
db.posts.last_edited.writable = False
db.bulletin_boards.last_edited.label = "Created On"

db.posts.bulletin_board.readable = db.posts.bulletin_board.writable = False
db.posts.user_id.default = auth.user_id
db.posts.user_id.readable = db.posts.user_id.writable = False
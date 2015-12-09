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

db.define_table('model',
                Field('name', 'string'),
                Field('description', 'text'),
                Field('tag_list', 'json'),
                Field('mesh_list', 'json'),
                Field('thumbnail_image', 'upload'),
                Field('isPublic', 'boolean', default=False),
                Field('isShareable', 'boolean', default=False),
                Field('num_favorites', 'integer', default=0),
                Field('last_edited', 'datetime', default=datetime.utcnow()),
                Field('user_id', db.auth_user, default=auth.user_id),
                Field('model_id', 'text')
                )

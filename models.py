from peewee import *

db = SqliteDatabase('./database.db')


class Media(Model):
    Name = TextField(unique=True)
    Path = TextField()
    Duration = IntegerField(null=False)
    Size = IntegerField(null=False)
    Type = TextField(null=False)
    Format = TextField(null=False)
    Date = DateTimeField()

    class Meta:
        database = db


db.create_tables([Media])

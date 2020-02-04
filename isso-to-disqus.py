#!/usr/bin/enc python3

import os
from peewee import *
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
from playhouse.migrate import *
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Init jinja2
env = Environment(
    loader=FileSystemLoader('./'),
    autoescape=select_autoescape(['html', 'xml'])
)

if 'WEBSITE_URL' not in os.environ or 'DB_FILE_PATH' not in os.environ:
    print('Please set the environment variables WEBSITE_URL and DB_FILE_PATH')
    sys.exit(1)

db = SqliteDatabase(os.environ.get('DB_FILE_PATH'))

# Define models according to Isso's db
# Some properties are missing because we won't import them in Disqus
class BaseModel(Model):
    class Meta:
        database = db

class Threads(BaseModel):
    uri = CharField()
    title = CharField()

class Comments(BaseModel):
    thread = ForeignKeyField(Threads, backref='comments')
    parent = IntegerField()
    created = FloatField()
    remote_addr = CharField()
    text = CharField()
    author = CharField()
    email = CharField()
    website = CharField()

    @property
    def created_time(self):
        return datetime.fromtimestamp(self.created)


db.connect()

print('Preparing database: renaming a column...')

if [comment for comment in db.get_columns('comments') if comment.name == 'thread_id'] == []:
    migrator = SqliteMigrator(db)
    # This fixes the foreign key when using the peewee model
    migrate(
        migrator.rename_column('comments', 'tid', 'thread_id'),
    )
else:
    print("Database already migrated.")


print('Getting titles from thread URLs...')
# For some reason the title column in the threads table was empty for me.
# Since this is a field that we need for Disqus, we'll fill this column now.
threads = Threads.select()

for thread in threads:
    # FYI I had to whitelist my IP because Cloudflare keeps returning 403s.
    # Using a proper UA would probably fix that.
    soup = BeautifulSoup(urlopen(os.environ.get('WEBSITE_URL') + thread.uri),features="html5lib")
    thread.title = soup.title.string
    thread.save()


print('Exporting comments to XML...')

comments = Comments.select()

template = env.get_template('template.xml.j2')
output = template.render(comments=comments,website_url=os.environ.get('WEBSITE_URL'))

with open("export.xml", "w") as fh:
    fh.write(output)

print("Done! Check export.xml")

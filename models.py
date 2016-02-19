from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types

class Account(messages.Message):
	username = messages.StringField(1,required=True)
	password = messages.StringField(2,required=True)
	email = messages.StringField(3,required=True)

class SignIn(messages.Message):
	email = messages.StringField(1,required=True)
	password = messages.StringField(2,required=True)

class Language(messages.Message):
	name = messages.StringField(1,required=True)
	mode = messages.StringField(2,required=True)
	ext = messages.StringField(3,required=True)
	compile = messages.StringField(4,required=True)
	execute = messages.StringField(5) 
	placeholder = messages.StringField(6)

class AccountModel(ndb.Model):
	username = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	fullname = ndb.StringProperty()
	country = ndb.StringProperty()

class LanguageModel(ndb.Model):
	name = ndb.StringProperty(required=True)
	mode = ndb.StringProperty(required=True)
	ext = ndb.StringProperty(required=True)
	compile = ndb.StringProperty(required=True)
	execute = ndb.StringProperty() 
	placeholder = ndb.StringProperty()

class Acknowledge(messages.Message):
	status = messages.BooleanField(1, required=True)
	comment = messages.StringField(2)
	data = messages.StringField(3, repeated=True)

class LanguageDetail(messages.Message):
	name = messages.StringField(1, required=True)
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

class Acknowledge(messages.Message):
	status = messages.BooleanField(1, required=True)
	comment = messages.StringField(2)
	data = messages.StringField(3, repeated=True)

class Query(messages.Message):
	name = messages.StringField(1)
	domain = messages.StringField(2)

class TestCase(messages.Message):
	test_in = messages.StringField(1, required=True)
	test_out = messages.StringField(2, required=True)
	points = messages.FloatField(3, required=True)
	ques_title = messages.StringField(4, required=True)

class TestCases(messages.Message):
	cases = messages.MessageField(TestCase, 1, repeated=True)

class Question(messages.Message):
	title = messages.StringField(1, required=True)
	text = messages.StringField(2, required=True)
	domain = messages.StringField(3, required=True)

class Questions(messages.Message):
	ques = messages.MessageField(Question, 1, repeated=True)

class QuestionModel(ndb.Model):
	title = ndb.StringProperty(required=True)
	text = ndb.StringProperty(required=True)
	domain = ndb.StringProperty(required=True)
	
class TestCaseModel(ndb.Model):
	test_in = ndb.StringProperty(required=True)
	test_out = ndb.StringProperty(required=True)
	points = ndb.FloatProperty(required=True)
	ques_title = ndb.StringProperty(required=True)

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
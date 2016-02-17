import endpoints

# from endpoints_proto_datastore.ndb import EndpointsModel
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from hashlib import md5

class Account(messages.Message):
	username = messages.StringField(1, required=True)
	password = messages.StringField(2, required=True)
	email = messages.StringField(3, required=True)

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

@endpoints.api(name='codegress',version='v1')
class CodegressApi(remote.Service):
	"""Codegress API v1"""

	@endpoints.method(Account, Acknowledge, 
		name='user.createAccount', path='user/create', http_method='POST')
	def create_account(self, request):
		ack = Acknowledge(status=False)
		account_key = ndb.Key('AccountModel',request.email)
		data = account_key.get()
		if not data:
			hashed_password = md5(request.password).hexdigest()
			account = AccountModel(username=request.username, password=hashed_password, email=request.email)
			account.key = account_key
			account.put()
			ack.status = True
		else:
			ack.comment = 'Email already taken'
		return ack

	@endpoints.method(SignIn, Acknowledge, name='user.check', path='user/check')
	def check_user(self, request):
		account_key = ndb.Key('AccountModel',request.email)
		ack = Acknowledge(status=False)
		if account_key:
			hashed_password = md5(request.password).hexdigest()
			if hashed_password == account_key.get().password:
				ack.status = True	
				ack.data = [request.email]
			else:
				ack.status = False
				ack.comment = hashed_password
		return ack

	@endpoints.method(Language, Acknowledge, name='language.insert', path='language/insert', http_method='POST')
	def insert_lang(self, request):
		ack = Acknowledge(status=False)
		lang_key = ndb.Key('LanguageModel',request.name)
		if not lang_key.get():
			new_lang = LanguageModel(name=request.name, mode=request.mode,ext=request.ext, 
				compile=request.compile, execute=request.execute, placeholder=request.placeholder)
			new_lang.key = lang_key
			new_lang.put()
			ack.status = True
		return ack

	@endpoints.method(LanguageDetail, Language, name='language.get',path='language/get')
	def get_lang(self, request):
		lang_key = ndb.Key('LanguageModel',request.name)
		lang = Language(name='',mode='',ext='',compile='',execute='',placeholder='')
		data = lang_key.get()
		if data:
			lang.name = data.name
			lang.mode = data.mode
			lang.ext = data.ext
			lang.compile = data.compile
			lang.execute = data.execute
			lang.placeholder = data.placeholder
		return lang


APPLICATION = endpoints.api_server([CodegressApi])
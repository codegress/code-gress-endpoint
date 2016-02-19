import endpoints

# from endpoints_proto_datastore.ndb import EndpointsModel  
from models import Account, AccountModel, Acknowledge, SignIn, Language, LanguageModel, LanguageDetail
from protorpc import remote
from hashlib import md5
from google.appengine.ext import ndb

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

	@endpoints.method(SignIn, Acknowledge, name='user.validateAccount', path='user/validate')
	def check_user(self, request):
		account_key = ndb.Key('AccountModel',request.email)
		ack = Acknowledge(status=False)
		data = account_key.get()
		if data:
			hashed_password = md5(request.password).hexdigest()
			if hashed_password == data.password:
				ack.status = True	
				ack.data = [request.email]
			else:
				ack.status = False
				ack.comment = hashed_password
		return ack

	@endpoints.method(SignIn, Acknowledge, name='user.removeAccount',path='user/remove')
	def remove_user(self,request):
		account_key = ndb.Key('AccountModel',request.email)
		ack = Acknowledge(status=False)
		data = account_key.get()
		if data:
			account_key.delete()
			ack.status = True
		return ack

	@endpoints.method(Language, Acknowledge, name='language.add', path='language/insert', http_method='POST')
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

	@endpoints.method(LanguageDetail, Acknowledge, name='language.remove',path='language/remove')
	def remove_lang(self,request):
		lang_key = ndb.Key('LanguageModel',request.name)
		ack = Acknowledge(status=False)
		data = lang_key.get()
		if lang_key.get():
			lang_key.delete()
			ack.status = True
		return ack

APPLICATION = endpoints.api_server([CodegressApi])
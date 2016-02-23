import endpoints

# from endpoints_proto_datastore.ndb import EndpointsModel  
from models import Account
from models import AccountModel
from models import Acknowledge
from models import Language
from models import LanguageModel
from models import LanguageDetail
from models import TestCase
from models import TestCases
from models import TestCaseModel
from models import SignIn
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
		user = AccountModel.query(ancestor=account_key).fetch()
		if not user:
			hashed_password = md5(request.password).hexdigest()
			account = AccountModel(parent=account_key,username=request.username, 
						password=hashed_password, email=request.email)
			account.put()
			ack.status = True
		elif user[0].username == request.username:
			ack.comment = 'Username already taken'
		elif user[0].email == request.email:
			ack.comment = 'Email already taken'
		else:
			ack.comment = 'Something went wrong..'
		return ack

	@endpoints.method(SignIn, Acknowledge, name='user.validateAccount', path='user/validate')
	def check_user(self, request):
		account_key = ndb.Key('AccountModel',request.email)
		ack = Acknowledge(status=False)
		data = AccountModel.query(ancestor=account_key).fetch()
		if data[0] and data[0].username:
			hashed_password = md5(request.password).hexdigest()
			if hashed_password == data[0].password:
				ack.status = True	
				ack.data = [request.email]
			else:
				ack.status = False
				ack.comment = hashed_password
		return ack

	# @endpoints.method(SignIn, Acknowledge, name='user.removeAccount',path='user/remove')
	# def remove_user(self,request):
	# 	account_key = ndb.Key('AccountModel',request.email)
	# 	ack = Acknowledge(status=False)
	# 	data = account_key.get()
	# 	if data:
	# 		account_key.delete()
	# 		ack.status = True
	# 	return ack

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

	@endpoints.method(TestCase, Acknowledge, name='testcase.add',path='testcase/add')
	def add_testcase(self, request):
		ack = Acknowledge(status = False)
		try:
			testcase_key = ndb.Key(TestCaseModel,request.ques_title)
			testcase = TestCaseModel(parent=testcase_key, test_in=request.test_in, test_out=request.test_out, 
					points=request.points, ques_title=request.ques_title)
			testcase.put()
			ack.status = True
		except:
			pass
		return ack

	@endpoints.method(LanguageDetail, TestCases, name='testcase.get',path='testcase/get')
	def get_testcase(self, request):
		testcase_key = ndb.Key(TestCaseModel,request.name)
		testcase_query = TestCaseModel.query(ancestor=testcase_key)
		testcases = testcase_query.fetch()
		testcase_list = []
		for testcase in testcases:
			case = TestCase(test_in=testcase.test_in, test_out=testcase.test_out, 
						ques_title=testcase.ques_title, points=testcase.points)
			testcase_list.append(case)
		return TestCases(cases=testcase_list)

APPLICATION = endpoints.api_server([CodegressApi])
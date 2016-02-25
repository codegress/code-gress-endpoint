import endpoints

# from endpoints_proto_datastore.ndb import EndpointsModel  
from models import Account
from models import AccountModel
from models import Acknowledge
from models import Language
from models import LanguageModel
from models import Query
from models import Question
from models import Questions
from models import QuestionModel
from models import TestCase
from models import TestCases
from models import TestCaseModel
from models import SignIn
from protorpc import remote
from hashlib import md5
from google.appengine.ext import ndb

@endpoints.api(name='codegress',version='v1')
class CodegressApi(remote.Service):
	"""Codegress Application API v1"""

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

	@endpoints.method(Language, Acknowledge, name='language.addLanguage', path='language/insert', http_method='POST')
	def insert_lang(self, request):
		ack = Acknowledge(status=False)
		lang_key = ndb.Key('LanguageModel',request.name)
		lang = LanguageModel.query(ancestor=lang_key).fetch()
		if not lang:
			new_lang = LanguageModel(parent=lang_key, name=request.name, mode=request.mode,ext=request.ext, 
				compile=request.compile, execute=request.execute, placeholder=request.placeholder)
			new_lang.put()
			ack.status = True
		return ack

	@endpoints.method(Query, Language, name='language.getLanguage',path='language/get')
	def get_lang(self, request):
		lang_key = ndb.Key('LanguageModel',request.name)
		lang = Language(name='',mode='',ext='',compile='',execute='',placeholder='')
		data = LanguageModel.query(ancestor=lang_key).fetch()
		if data and data[0]:
			lang.name = data[0].name
			lang.mode = data[0].mode
			lang.ext = data[0].ext
			lang.compile = data[0].compile
			lang.execute = data[0].execute
			lang.placeholder = data[0].placeholder
		return lang

	@endpoints.method(Question, Acknowledge, name='question.addQuestion', path='question/add')
	def add_question(self, request):
		ack = Acknowledge(status=False)
		domain_key = ndb.Key('Domain', request.domain)
		ques_key = ndb.Key(QuestionModel,request.title, parent=domain_key)
		ques = QuestionModel.query(ancestor=ques_key).fetch()
		if not ques:
			ques = QuestionModel(parent=ques_key,title=request.title, text=request.text, domain=request.domain)
			ques.put()
			ack.status = True
		return ack

	@endpoints.method(Query, Questions, name='question.getDomainQuestion', path='question/domain/get')
	def get_domain_questions(self, request):
		domain_key = ndb.Key('Domain', request.domain)
		ques_query = QuestionModel.query(ancestor=domain_key).fetch()
		ques_list = []
		for q in ques_query:
			current_ques = Question(title=q.title, text=q.text, domain=q.domain)
			ques_list.append(current_ques)
		return Questions(ques=ques_list)

	@endpoints.method(Query, Question, name='question.getQuestion', path='question/get')
	def get_question(self,request):
		domain_key = ndb.Key('Domain', request.domain)
		ques_key = ndb.Key(QuestionModel, request.name, parent=domain_key)
		ques_query = QuestionModel.query(ancestor=ques_key).fetch()
		ques = Question(title=request.name, text='', domain=request.domain)
		for q in ques_query:
			ques.text = q.text
		return ques

	@endpoints.method(TestCase, Acknowledge, name='testcase.addTestcase',path='testcase/add')
	def add_testcase(self, request):
		testcase_key = ndb.Key(TestCaseModel,request.ques_title)
		testcase = TestCaseModel(parent=testcase_key, test_in=request.test_in, test_out=request.test_out, 
				points=request.points, ques_title=request.ques_title)
		testcase.put()
		return Acknowledge(status=True)

	@endpoints.method(Query, TestCases, name='testcase.getTestcase',path='testcase/get')
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
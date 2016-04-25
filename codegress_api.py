import endpoints
import re
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
from models import CommentModel 
from models import ChallengeModel
from models import ChallengeFeedModel
from models import FollowModel
from models import Follow
from models import Follower
from protorpc import remote
from hashlib import md5
from datetime import datetime

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
		username = AccountModel.query(AccountModel.username == request.username).fetch()
		if username or user:
			if username:
				ack.data += ['username']
			if user:
				ack.data += ['email']
		else:
			hashed_password = md5(request.password).hexdigest()
			account = AccountModel(parent=account_key,username=request.username, 
						password=hashed_password, email=request.email)
			account.put()
			ack.status = True
		return ack

	@endpoints.method(SignIn, Acknowledge, name='user.validateAccount', path='user/validate')
	def check_user(self, request):
		account_key = ndb.Key('AccountModel',request.email)
		ack = Acknowledge(status=False)
		user = AccountModel.query(ancestor=account_key).fetch()
		if not user:
			user = AccountModel.query(AccountModel.username == request.email).fetch()
		if user:
			hashed_password = md5(request.password).hexdigest()
			if hashed_password == user[0].password:
				ack.data = [user[0].username]	
				ack.status = True
			else:
				ack.data += ["password"]
		else:
			ack.data += ["username"]
		return ack

	@LanguageModel.method(name='language.addLanguage', path='language/insert', http_method='POST')
	def insert_lang(self,language):
		language.put()
		return language

	@LanguageModel.query_method(query_fields=('name',),name='language.getLanguage',path='language/get')
	def get_lang(self, language_query):
		return language_query

	@QuestionModel.method(name='question.addQuestion', path='question/add', http_method='POST')
	def add_question(self, question_instance):
		domain_key = ndb.Key('Domain', question_instance.domain)
		ques_key = ndb.Key(QuestionModel, question_instance.title, parent=domain_key)
		ques = QuestionModel.query(QuestionModel.domain == question_instance.domain, QuestionModel.title==question_instance.title).fetch()
		if not ques:
			question_instance.parent = ques_key
			question_instance.put()
		else:
			question_instance = ques[0]
		return question_instance 

	@QuestionModel.method(request_fields=('title','domain','likes'),name='question.addQuestionLike', path='question/like/add')
	def add_question_like(self, question_instance):
		ques = QuestionModel.query(QuestionModel.domain == question_instance.domain, QuestionModel.title==question_instance.title).fetch()
		if ques:
			likes = ques[0].likes
			for username in likes.username:
				if username == question_instance.likes.username:
					return question_instance
			if likes:
				ques[0].likes += question_instance.likes
			else:
				ques[0].likes = question_instance.likes
			ques[0].put()
		return question_instance
	
	@QuestionModel.method(request_fields=('title','domain','comments'),name='question.addQuestionComment', path='question/comment/add')
	def add_question_comment(self, question_instance):
		ques = QuestionModel.query(QuestionModel.domain == question_instance.domain, QuestionModel.title==question_instance.title).fetch()
		if ques:
			if ques[0].comments:
				ques[0].comments += question_instance.comments
			else:
				ques[0].comments = question_instance.comments
			ques[0].put()
		return question_instance

	@QuestionModel.query_method(query_fields=('domain',),name='question.getDomain', path='domain/get')
	def get_domain_question(self, domain_query):
		return domain_query

	@QuestionModel.query_method(query_fields=('title',),name='question.getQuestion', path='question/get')
	def get_question(self, question_query):
		return question_query

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

	@endpoints.method(Query, Acknowledge, name='user.shortListed', path='user/shortlist')
	def get_shortlisted_users(self,request):
		shortListed_users = []
		accounts = AccountModel.query(AccountModel.username == request.name).fetch()
		if not accounts:
			accounts = AccountModel.query(AccountModel.username >= request.name).fetch()
			for account in accounts:
				if re.match(request.name, account.username , re.I):
					shortListed_users.append(account.username)
		else:
			shortListed_users.append(accounts[0].username)
		return Acknowledge(data=shortListed_users, status=True)
	
	@endpoints.method(Follow, Follow,name='user.follow',path='user/follow')
	def add_follow(self, request):
		follow_instance = Follow()
		followee_key = ndb.Key(FollowModel, request.followee)
		acc_follower = AccountModel.query(AccountModel.username == request.follower).fetch()
		acc_followee = AccountModel.query(AccountModel.username == request.followee).fetch()
		if acc_follower and acc_followee:
			follow = FollowModel.query(FollowModel.follower==request.follower,
				FollowModel.followee==request.followee).fetch()
			if not follow:
				follow = FollowModel(follower=acc_follower[0].username, followee=acc_followee[0].username, parent=followee_key).put()
				follow_instance.follower=request.follower
				follow_instance.followee=request.followee
		return follow_instance

	@endpoints.method(Query, Follower,name='user.getFollowers',path='user/get/followers')
	def get_followers(self, request):
		followee_key = ndb.Key(AccountModel, request.name)
		follower = AccountModel.query(AccountModel.username == request.name).fetch()
		followers = Follower()
		if follower:
			follow_query = FollowModel.query(FollowModel.followee == request.name).fetch()
			follow_list = []
			for follow in follow_query:
				follow_list += [follow.follower]
			followers.names = follow_list
		return followers

	@endpoints.method(Query, Follower,name='user.getFollowees',path='user/get/followees')
	def get_followees(self, request):
		follow_key = ndb.Key(FollowModel, request.name)
		followee = AccountModel.query(AccountModel.username == request.name).fetch()
		followers = Follower()
		if followee:
			follow_query = FollowModel.query(FollowModel.follower == request.name).fetch()
			follow_list = []
			for follow in follow_query:
				follow_list += [follow.followee]
			followers.names = follow_list
		return followers

	# @SubmissionModel.method(request_fields=('ques_title','submission_text','submitted_user'),
	# 	name='submission.addSubmission',path='submission/add',http_method='POST')
	# def add_submission(self,submission):
	# 	submission.submission_date = datetime.now()
	# 	submission.put()
	# 	return submission
	
	# @SubmissionModel.query_method(query_fields=('ques_title','submitted_user'),name='submission.getSubmission',path='submission/get')
	# def get_submission(self,submission_query):
	# 	return submission_query

	# @ChallengeFeedModel.method(name='challenge.addChallengeFeed',path='challenge/add/challengefeed')
	# def add_challenge_feed(self, challenge_feed_instance):
	# 	ques_key = ndb.Key(QuestionModel, challenge_feed_instance.ques_title)
	# 	user_key = ndb.Key(AccountModel, challenge_feed_instance.username, parent=ques_key)
	# 	existing_challenge_feed = ChallengeFeedModel.query(ChallengeFeedModel.ques_title == challenge_feed_instance.ques_title, 
	# 							ChallengeFeedModel.username == challenge_feed_instance.username).fetch()
	# 	if existing_challenge_feed:
	# 		if existing_challenge_feed[0].comment:
	# 			existing_challenge_feed[0].comment.append(challenge_feed_instance.comment)
	# 		else:
	# 			existing_challenge_feed[0].comment = challenge_feed_instance.comment
	# 		existing_challenge_feed[0].like = challenge_feed_instance.like
	# 		existing_challenge_feed[0].put()
	# 	else:
	# 		ques_key = ndb.Key(QuestionModel, challenge_feed_instance.ques_title)
	# 		user_key = ndb.Key(AccountModel, challenge_feed_instance.username, parent=ques_key)
	# 		challenge_feed_instance.parent = user_key
	# 		challenge_feed_instance.put()
	# 	return challenge_feed_instance


	@ChallengeModel.method(name='challenge.addChallenge',path='challenge/add')
	def add_challenge(self, challenge_instance):
		already_challenged = ChallengeModel.query(ChallengeModel.ques_title == challenge_instance.ques_title, 
			ChallengeModel.challenger == challenge_instance.challenger, ChallengeModel.challengee == challenge_instance.challengee).fetch()
		if not already_challenged:
			challenge_instance.datetime = datetime.now()
			challenge_instance.parent = ndb.Key(ChallengeModel, challenge_instance.ques_title)
			challenge_instance.seen = False
			challenge_instance.accepted = False
			challenge_instance.solved = False
			challenge_instance.put()
		return challenge_instance

	@ChallengeModel.query_method(query_fields=('challenger',),name='challenge.getChallenged',path='challenge/get/challenged')
	def get_challenged_challenges(self, challenge_query):
		return challenge_query

	@ChallengeModel.query_method(query_fields=('challengee',),name='challenge.getChallenges',path='challenge/get/challenges')
	def get_challenges(self, challenge_query):
		return challenge_query

APPLICATION = endpoints.api_server([CodegressApi])
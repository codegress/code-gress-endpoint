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
from models import SubmissionModel
from models import ChallengeFeed
from models import ChallengeFeeds
from models import ChallengeFeedModel
from models import CommentModel
from models import ChallengeModel
from models import UserChallengeModel
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

	@endpoints.method(Question, Acknowledge, name='question.addQuestion', path='question/add', http_method='POST')
	def add_question(self, request):
		ack = Acknowledge(status=False)
		domain_key = ndb.Key('Domain', request.domain)
		ques_key = ndb.Key(QuestionModel, request.title, parent=domain_key)
		ques = QuestionModel.query(ancestor=ques_key).fetch()
		if not ques:
			ques = QuestionModel(parent=ques_key, title=request.title, text=request.text, domain=request.domain)
			ques.put()
			ack.status = True
		return ack

	@endpoints.method(Query, Questions, name='question.getQuestion', path='question/get')
	def get_question(self,request):
		ancestor_key = None
		if request.domain:
			ancestor_key = ndb.Key('Domain', request.domain)
			if request.name:
				ancestor_key = ndb.Key(QuestionModel, request.name, parent=ancestor_key)
			ques_query = QuestionModel.query(ancestor=ancestor_key).fetch()
		else:
			ques_query = QuestionModel.query().fetch()
		ques_list = []
		for q in ques_query:
			ques = Question(title=q.title, text=q.text, domain=q.domain)
			ques_list += [ques]
		return Questions(ques=ques_list)

	@endpoints.method(TestCase, Acknowledge, name='testcase.addTestcase',path='testcase/add',http_method='POST')
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
		accounts = AccountModel.query(AccountModel.username >= request.name).fetch()
		for account in accounts:
			matched = re.match(request.name, account.username , re.I)
			if matched:
				shortListed_users.append(account.username)
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

	@SubmissionModel.method(request_fields=('ques_title','submission_text','submitted_user'),
		name='submission.addSubmission',path='submission/add',http_method='POST')
	def add_submission(self,submission):
		submission.submission_date = datetime.now()
		submission.put()
		return submission
	
	@SubmissionModel.query_method(query_fields=('ques_title','submitted_user'),name='submission.getSubmission',path='submission/get')
	def get_submission(self,submission_query):
		return submission_query

	@ChallengeFeedModel.method(name='challenge.addFeed', path='challenge/add/feed')
	def add_feed_challenges(self, challenge_feed):
		request_user = None
		if challenge_feed.likes:
			request_user = challenge_feed.likes[0]
		if not request_user:
			request_user = challenge_feed.comments[0].username

		question = QuestionModel.query(QuestionModel.title == challenge_feed.ques_title).fetch()
		account = AccountModel.query(AccountModel.username == request_user).fetch()
		feed = None
		if question and account:
			feed = ChallengeFeedModel.query(ChallengeFeedModel.ques_title == challenge_feed.ques_title).fetch()

		if feed:
			user = account[0].username
			if feed[0].likes and challenge_feed.likes:
				feed[0].likes += [user]
			if challenge_feed.comments:
				feed_comment = challenge_feed.comments[0]
				feed_comment.datatime = datetime.now()
				feed[0].comments += [feed_comment]
			feed[0].put()
		else:
			challenge_feed.comments[0].datetime = datetime.now()
			challenge_feed.put()
		return challenge_feed

	# @endpoints.method(Query, ChallengeFeeds, name='challenge.getFeeds',path='challenge/get/feeds')
	# def get_feed_challenges(self,request):
	# 	request_user = request.name
	# 	account = AccountModel.query(AccountModel.username == request_user).fetch()
	# 	if account:
	# 		feeds = ChallengeFeedModel.query(ChallengeFeedModel.username == request_user).fetch()
	# 		challenge_feeds = []
	# 		for feed in feeds:
	# 			challenge_feed = ChallengeFeed(ques_title=feed.ques_title,username=request_user,like=feed.like)

	@UserChallengeModel.method(name='user.addChallenge',path='user/add/challenge')
	def add_user_challenge(self, user_challenge):
		user_challenge.challenge.start_date = datetime.now()
		user_challenge.put()
		return user_challenge

	@ChallengeModel.query_method(query_fields=('challenger','challengee'),name='user.getChallenge',path='user/get/challenge')
	def get_user_challenge(self, user_challenge_query):
		return user_challenge_query

APPLICATION = endpoints.api_server([CodegressApi])
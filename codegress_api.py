import endpoints
from google.appengine.ext import ndb
import re
from models import Account
from models import AccountModel 
from models import Acknowledgement
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
from models import Like
from models import Comment
from models import ChallengeFeed
from models import ChallengeFeeds
from models import FollowModel
from models import Follow
from models import Follower 
from models import MessageModel
from protorpc import remote
from hashlib import md5
from datetime import datetime
from google.appengine.ext import ndb

@endpoints.api(name='codegress',version='v1')
class CodegressApi(remote.Service):
	"""Codegress Application API v1"""

	@endpoints.method(Account, Acknowledgement, 
		name='user.createAccount', path='user/create', http_method='POST')
	def create_account(self, request):
		ack = Acknowledgement(status=False)
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

	@endpoints.method(SignIn, Acknowledgement, name='user.validateAccount', path='user/validate')
	def check_user(self, request):
		account_key = ndb.Key('AccountModel',request.email)
		ack = Acknowledgement(status=False)
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
	def add_question_like(self, q_instance):
		ques = QuestionModel.query(QuestionModel.domain == q_instance.domain, QuestionModel.title==q_instance.title).fetch()
		if ques:
			if ques[0].likes:
				for q in ques[0].likes:
					if q.username == q_instance.likes[0].username:
						return q_instance
				ques[0].likes += q_instance.likes
			else:
				ques[0].likes = q_instance.likes
			ques[0].put()
		return q_instance
	
	@QuestionModel.method(request_fields=('title','domain','comments'),name='question.addQuestionComment', path='question/comment/add')
	def add_question_comment(self, question_instance):
		ques = QuestionModel.query(QuestionModel.domain == question_instance.domain, QuestionModel.title==question_instance.title).fetch()
		if ques:
			if ques[0].comments:
				ques[0].comments += question_instance.comments
			else:
				ques[0].comments = question_instance.comments
			ques[0].put()
			return ques[0]
		return question_instance

	@QuestionModel.query_method(query_fields=('domain',),name='question.getDomain', path='domain/get')
	def get_domain_question(self, domain_query):
		return domain_query

	@QuestionModel.query_method(query_fields=('title',),name='question.getQuestion', path='question/get')
	def get_question(self, question_query):
		return question_query

	@endpoints.method(TestCase, Acknowledgement, name='testcase.addTestcase',path='testcase/add')
	def add_testcase(self, request):
		testcase_key = ndb.Key(TestCaseModel,request.ques_title)
		testcase = TestCaseModel(parent=testcase_key, test_in=request.test_in, test_out=request.test_out, 
				points=request.points, ques_title=request.ques_title)
		testcase.put()
		return Acknowledgement(status=True)

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

	@endpoints.method(Query, Acknowledgement, name='user.shortListed', path='user/shortlist')
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
		return Acknowledgement(data=shortListed_users, status=True)
	
	@FollowModel.method(name='user.follow',path='user/follow')
	def add_follow(self, follow_instance):
		followee_key = AccountModel.key(AccountModel, follow_instance.followee)
		acc_followee = AccountModel.query(AccountModel.username == follow_instance.followee).fetch()
		acc_follower = AccountModel.query(AccountModel.username == follow_instance.follower).fetch()
		if acc_follower and acc_followee:
			follow = FollowModel.query(FollowModel.follower == follow_instance.follower,
				FollowModel.followee == follow_instance.followee).fetch()
			if not follow:
				follow_instance.parent = followee_key
				follow_instance.put()
		return follow_instance

	@endpoints.method(Query, Acknowledgement, name='user.getFollowSuggestions',path='user/get/follows')
	def get_follows(self, request):
		ack = Acknowledgement(status=False)
		follows = AccountModel.query(AccountModel.username != request.name).fetch()
		follow_list = []
		for follow in follows:
			follow_list.append(follow.username)
		if follow_list:
			ack.status = True
			ack.data = follow_list
		return ack

	@FollowModel.query_method(query_fields=('follower',) ,name='user.getFollowers',path='user/get/followers')
	def get_followers(self, follower_query):
		return follower_query

	@FollowModel.query_method(query_fields=('followee',) ,name='user.getFollowees',path='user/get/followees')
	def get_followees(self, followee_query):
		return followee_query

	@ChallengeModel.method(name='challenge.addChallenge',path='challenge/add')
	def add_challenge(self, challenge_instance):
		ques = QuestionModel.query(QuestionModel.title == challenge_instance.ques.title).fetch()
		already_challenged = ChallengeModel.query(ChallengeModel.ques.title == ques[0].title, ChallengeModel.challenger == challenge_instance.challenger,
							ChallengeModel.challengee == challenge_instance.challengee).fetch()
		if not already_challenged:
			challenge_instance.datetime = datetime.now()
			challenge_instance.parent = ndb.Key(ChallengeModel, challenge_instance.ques.title)
			challenge_instance.seen = False
			challenge_instance.accepted = False
			challenge_instance.solved = False
			challenge_instance.rejected = False
			challenge_instance.put()
		return challenge_instance

	@ChallengeModel.method(name='challenge.modify', path='challenge/modify')
	def solved_challenge(self, challenge_instance):
		ques = QuestionModel.query(QuestionModel.title == challenge_instance.ques.title).fetch()
		already_challenged = ChallengeModel.query(ChallengeModel.ques.title == ques[0].title, ChallengeModel.challenger == challenge_instance.challenger,
							ChallengeModel.challengee == challenge_instance.challengee).fetch() 
		if already_challenged:
			already_challenged[0].seen = challenge_instance.seen
			already_challenged[0].accepted = challenge_instance.accepted
			already_challenged[0].solved = challenge_instance.solved
			already_challenged[0].rejected = challenge_instance.rejected
			already_challenged[0].put()
		return already_challenged[0]

	@ChallengeModel.method(name='challenge.addLike',path='challenge/add/like')
	def add_challenge_like(self, c_ins):
		ques = QuestionModel.query(QuestionModel.title == c_ins.ques.title, QuestionModel.domain == c_ins.ques.domain).fetch()
		if ques:
			challenge = ChallengeModel.query(ChallengeModel.challenger == c_ins.challenger, 
				ChallengeModel.challengee == c_ins.challengee).fetch()
			for c in challenge:
				if c.ques.title == c_ins.ques.title:
					likes = c.likes
					for like in likes:
						if like.username == c_ins.likes[0].username:
							return c
					c.likes += c_ins.likes
					c.put()
					return c
		return c_ins

	@ChallengeModel.query_method(query_fields=('challenger',),name='challenge.getChallenged',path='challenge/get/challenged')
	def get_challenged_challenges(self, challenge_query):
		return challenge_query

	@ChallengeModel.query_method(query_fields=('challengee',),name='challenge.getChallenges',path='challenge/get/challenges')
	def get_challenges(self, challenge_query):
		return challenge_query


	@MessageModel.method(name='message.send', path='message/send')
	def send_message(self, message_instance):
		message_instance.datetime=datetime.now()
		message_instance.read = False
		message_instance.put()
		return message_instance

	@MessageModel.query_method(query_fields=('frm',), name='message.getMessageFrom',path='message/get/from')
	def get_message_frm(self, message_query):
		return message_query.order(-MessageModel.datetime)
	
	@MessageModel.query_method(query_fields=('to',), name='message.getMessageTo',path='message/get/to')
	def get_message_to(self, message_query):
		return message_query.order(-MessageModel.datetime)

	@MessageModel.query_method(query_fields=('to','read'), name='message.getMessageRead',path='message/get/read')
	def get_message_read(self, message_query):
		return message_query.order(-MessageModel.datetime)

	@MessageModel.method(name='message.readTrue', path='message/read/true')
	def read_true_message(self, msg_instance):
		messages = MessageModel.query(MessageModel.to == msg_instance.to, MessageModel.read == False).order(-MessageModel.datetime)
		for m in messages:
			m.read = True
			m.put()
		return msg_instance

	@endpoints.method(Query, ChallengeFeeds, name='challenge.getChallengeFeeds', path='challenge/get/challenge/feeds')
	def get_challenge_feeds(self, request):
		f_list = FollowModel.query(FollowModel.follower == request.name).fetch()
		challenge_list = []
		liked_by_user = False
		for f in f_list:
			followee = f.followee
			challenges = ChallengeModel.query(ndb.OR(ChallengeModel.challenger == followee, ChallengeModel.challengee == followee)).order(-ChallengeModel.datetime)
			for challenge in challenges:
				if challenge.challengee == request.name or challenge.challenger == request.name:
					continue
				ques = challenge.ques
				likes = challenge.ques.likes
				comments = challenge.ques.comments
				c_likes = challenge.likes
				ques_like_list, ch_like_list, comment_list = [], [], [] 
				for c in c_likes:
					if c.username == request.name:
						liked_by_user = True
					new_like = Like(username=c.username, liked=c.liked)
					ch_like_list.append(new_like)
				for l in likes:
					new_like = Like(username=l.username, liked=l.liked)
					ques_like_list.append(new_like)
				for c in comments:
					new_comment = Comment(username=c.username, datetime=c.datetime, comment_message=c.comment_message)
					comment_list.append(new_comment)
				new_question = Question(title=ques.title, text=ques.text, domain=ques.domain, likes=ques_like_list, comments=comment_list)
				new_challenge = ChallengeFeed(liked_by_user=liked_by_user,likes=ch_like_list, ques=new_question, challengee=challenge.challengee, challenger=challenge.challenger, datetime=challenge.datetime)
				challenge_list.append(new_challenge)
		return ChallengeFeeds(feeds=challenge_list)

APPLICATION = endpoints.api_server([CodegressApi])
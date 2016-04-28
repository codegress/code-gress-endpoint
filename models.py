from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from endpoints_proto_datastore.ndb import EndpointsModel  

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

class ChallengeFeed(messages.Message):
	ques_title = messages.StringField(1, required=True)
	username = messages.StringField(2)
	like = messages.BooleanField(3)
	comment = messages.StringField(4)

class ChallengeFeeds(messages.Message):
	feeds = messages.MessageField(ChallengeFeed,1,repeated=True)

class Follow(messages.Message):
	follower = messages.StringField(1)
	followee = messages.StringField(2)

class Follower(messages.Message):
	names = messages.StringField(1,repeated=True)

class AccountModel(ndb.Model):
	username = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	fullname = ndb.StringProperty()
	country = ndb.StringProperty()

class LanguageModel(EndpointsModel):
	name = ndb.StringProperty(required=True)
	mode = ndb.StringProperty(required=True)
	ext = ndb.StringProperty(required=True)
	compile = ndb.StringProperty(required=True)
	execute = ndb.StringProperty() 
	placeholder = ndb.StringProperty()

class CommentModel(EndpointsModel):
	username = ndb.StringProperty(required=True)
	datetime = ndb.DateTimeProperty(auto_now=True)
	comment_message = ndb.StringProperty(required=True)

class LikeModel(EndpointsModel):
	username = ndb.StringProperty(required=True)
	liked = ndb.BooleanProperty(required=True)

class QuestionModel(EndpointsModel):
	title = ndb.StringProperty(required=True)
	text = ndb.StringProperty()
	domain = ndb.StringProperty(required=True)
	likes = ndb.StructuredProperty(LikeModel, repeated=True)
	comments = ndb.StructuredProperty(CommentModel, repeated=True)
	
class TestCaseModel(ndb.Model):
	test_in = ndb.StringProperty(required=True)
	test_out = ndb.StringProperty(required=True)
	points = ndb.FloatProperty(required=True)
	ques_title = ndb.StringProperty(required=True)


# class SubmissionModel(EndpointsModel):
# 	ques_title = ndb.StringProperty(required=True)
# 	submission_text = ndb.TextProperty()
# 	submission_date = ndb.DateTimeProperty()
# 	submitted_user = ndb.StringProperty(required=True)

class MessagesModel(EndpointsModel):
	message = ndb.StringProperty(required=True)
	datetime = ndb.DateTimeProperty()
	frm = ndb.StringProperty(required=True)
	to = ndb.StringProperty(required=True)

class ChallengeModel(EndpointsModel):
	ques = ndb.StructuredProperty(QuestionModel, required=True)
	challenger = ndb.StringProperty(required=True)
	challengee = ndb.StringProperty(required=True)
	datetime = ndb.DateTimeProperty()
	seen = ndb.BooleanProperty()
	accepted = ndb.BooleanProperty()
	solved = ndb.BooleanProperty()
	rejected = ndb.BooleanProperty()

# class UserChallengeModel(EndpointsModel):
# 	challenge = ndb.StructuredProperty(ChallengeModel,required=True)
# 	state = ndb.StringProperty(choices=['Accept','Reject'],required=True)

# class UserChallengerModel(ndb.Model):
# 	challenge = ndb.StructuredProperty(ChallengeModel, required=True)
# 	challenger = ndb.StructuredProperty(AccountModel, required=True)
# 	challengee = ndb.StructuredProperty(AccountModel, required=True)

class ChallengeFeedModel(EndpointsModel):
	ques_title = ndb.StringProperty()
	username = ndb.StringProperty()
	like = ndb.BooleanProperty()
	comment = ndb.StructuredProperty(CommentModel,repeated=True)
	
class FollowModel(ndb.Model):
	follower = ndb.StringProperty(required=True)
	followee = ndb.StringProperty(required=True)
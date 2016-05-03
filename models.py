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

class Acknowledgement(messages.Message):
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

class Like(messages.Message):
	username = messages.StringField(1, required=True)
	liked = messages.BooleanField(2, required=True)

class Comment(messages.Message):
	username = messages.StringField(1, required=True)
	datetime = message_types.DateTimeField(2, required=True)
	comment_message = messages.StringField(3, required=True)

class Question(messages.Message):
	title = messages.StringField(1, required=True)
	text = messages.StringField(2, required=True)
	domain = messages.StringField(3, required=True)
	likes = messages.MessageField(Like, 4, repeated=True)
	comments = messages.MessageField(Comment, 5, repeated=True)

class Questions(messages.Message):
	ques = messages.MessageField(Question, 1, repeated=True)

class ChallengeFeed(messages.Message):
	ques = messages.MessageField(Question, 1)
	challenger = messages.StringField(2,)
	challengee = messages.StringField(3)
	datetime = message_types.DateTimeField(4)

class ChallengeFeeds(messages.Message):
	feeds = messages.MessageField(ChallengeFeed, 1, repeated=True)

class Follow(messages.Message):
	follower = messages.StringField(1)
	followee = messages.StringField(2)

class Follower(messages.Message):
	names = messages.MessageField(Follow, 1, repeated=True)

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
	
class TestCaseModel(EndpointsModel):
	test_in = ndb.StringProperty()
	test_out = ndb.StringProperty()
	points = ndb.FloatProperty(required=True)
	ques = ndb.StructuredProperty(Question, required=True)

class MessageModel(EndpointsModel):
	message = ndb.StringProperty(required=True)
	datetime = ndb.DateTimeProperty()
	frm = ndb.StringProperty(required=True)
	to = ndb.StringProperty(required=True)
	read = ndb.BooleanProperty()
 
class ChallengeModel(EndpointsModel):
	ques = ndb.StructuredProperty(QuestionModel, required=True)
	challenger = ndb.StringProperty(required=True)
	challengee = ndb.StringProperty(required=True)
	datetime = ndb.DateTimeProperty()
	seen = ndb.BooleanProperty()
	accepted = ndb.BooleanProperty()
	solved = ndb.BooleanProperty()
	rejected = ndb.BooleanProperty()

class FollowModel(EndpointsModel):
	follower = ndb.StringProperty(required=True)
	followee = ndb.StringProperty(required=True)
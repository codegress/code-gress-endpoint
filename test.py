from hashlib import md5
import re

class Account(object):
	def __init__(self, name, password, email):
		self.email = self.validate(email)
		if self.email:
			self.name = name
			self.password = self.generate_hash(password)

	def __str__(self):
		if self.email:
			return "Username : %s\nPassword : %s\nEmail : %s" %(self.name,self.password,self.email)
		return "Account declined!!"

	def generate_hash(self,password):
		return md5(password).hexdigest()

	def validate(self,email):
		regex = "^[a-z0-9]+\@[a-z]+\.(?:[a-z]{3}|[a-z]{2}\.[a-z]{2})$"
		if re.findall(regex, email):
			return email

print Account("rgetty","jingle","rgetty6@gmail.com")
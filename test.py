from hashlib import md5
import re
users = ['teju','xyz','twxy','tetty','taw','tew']
def search(text):
	new_user=[]
	for user in users:
		matchObj = re.match(text, user , re.M|re.I)
		if matchObj:
			new_user.append(user) 

	return new_user

print search("tej")
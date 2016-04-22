import re
username = 'rgetty'
accounts = ['rgetty','rgetty6','rgty','teja','teju','iminion']
short_list = []
for account in accounts:
	if re.match(username, account, re.I):
		short_list.append(account)
print short_list
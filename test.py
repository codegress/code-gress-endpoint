import smtplib
server = smtplib.SMTP('smtp.gmail.com',587)
server.ehlo()
server.starttls()
server.login("codegres@gmail.com","coder123")
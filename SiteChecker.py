#Check Favorite Sites are Up
import requests
import multiprocessing as mp
from multiprocessing import Queue
import time
import base64
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

base64.b64decode("R01BSUxzZXAyMw==")
#Timeout is the number of seconds that a request can take before it is considered to timeout.
timeout = 3
#RequestCooldown is the number of seconds between each wave of requests to the website
requestCooldown = 15

#Whenever a request returns something other than response code 200, an email is sent. 
#emailCooldown dictates how long must pass between each email for that website.
emailCooldown = 1800
workers = [] # Worker Processes
siteQueue = Queue() 
sitesList = []

userEmailAddress = "danjin250@gmail.com"
userEmailPassword = base64.b64decode("R01BSUxzZXAyMw==")
#Don't worry, the email address/password are not saved anywhere. They would only be visible in the .py file!

user_agent = {'User-agent': 'Mozilla/5.0'}
server = smtplib.SMTP('smtp.gmail.com',587)
server.ehlo()
server.starttls()
server.login(userEmailAddress, userEmailPassword)
fromaddr = userEmailAddress
toaddr = userEmailPassword


#-------------------------------------------------------
#Functions
#Site_status(url)bb
# Url: a site url to be checked
def site_status(url):
	try:
		r = requests.get(url,timeout = timeout, headers=user_agent)
		return r.status_code
	except Exception as e:
		return e.message





def worker(siteQueue):
	currentTime = time.time()
	firstEmail = True
	if not siteQueue.empty():
		url = siteQueue.get()
		while(True):
			responseCode = site_status(url)
			if(responseCode == requests.codes.ok):
				print(url+ ' is good!')
			else:
				print responseCode
				print(url + ' gave error ' + str(responseCode))
				elapsedTime = time.time() - currentTime
				print(str(elapsedTime) + " elapsed")
				if(elapsedTime > emailCooldown or firstEmail):
					firstEmail = False
					print("An email was sent for " + url)
					sendEmail(url, responseCode)
					currentTime = time.time()
			time.sleep(requestCooldown)		


def sendEmail(url, errorCode):
	errorCode = str(errorCode)
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Downed Notice from AreTheyUp"
	body = "This email is to inform you that " + url + " just returned with error code " + errorCode
	msg.attach(MIMEText(body, 'plain'))
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	
	
if __name__ == '__main__':
#=========================================================
#Grabbing Input
	print("Welcome to AreTheyUp")
	print("Options: \n 1: Add Websites to Check \n 2: Load Previously Used Sites \n 3: View the list of Saved Sites \n 4: Delete list of Saved Sites")
	tries = 0
	while(tries < 10):
		talkToMe = raw_input("What do you want to do?: ")
		tries+=1
		if talkToMe == "1":
			textFile = open('sites.txt', 'r+')
			urls = textFile.read()
			if(urls):
				sitesList = urls.split(',')
				sitesList.remove('')
			textFile.close()
			textFile = open('sites.txt', 'a')
			while(True):
				site = raw_input("Tell me a site to add (stop to stop): ")
				if(site.lower() == 'stop'):
					break
				else:
					if not (site.startswith('https://') or site.startswith('http://')):
							site = "http://"+ site
					sitesList.append(site)
					textFile.write(site+",")
			textFile.close()
			break			
		elif talkToMe == "2":
			textFile = open('sites.txt', 'r+')
			urls = textFile.read()
			sitesList = urls.split(',')
			sitesList.remove('')
		  	break
		
		elif talkToMe == "3":
			textFile = open('sites.txt', 'r')
			urls = textFile.read()
			sitesList = urls.split(',')
			sitesList.remove('')
			print("The current list of saved sites: ")
			print sitesList
			sitesList = []
			continue
			
		elif talkToMe == "4":
			open('sites.txt', 'w').close()
			print("Saved websites list successfully deleted.")
			continue
		
		else:
			print("That's not a valid choice. Try again.")
			if(tries == 9):
				print("Invalid choice inputted too many times. Program closing.")
				break
			continue
		
			
#---------------------------------------------------------------
# Processing and actual Site stuff
	for site in sitesList:
		siteQueue.put(site)

	for x in xrange(len(sitesList)):
		p =  mp.Process(target = worker, args = (siteQueue,))
		workers.append(p)
		p.start()




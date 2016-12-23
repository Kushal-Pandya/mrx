

import requests
import main
import time


"""
   __
  /__)  _  _     _   _ _/_  _
 / (   (- (/ (/ (- _)  /  _)
          /


CURL COMMAND:
~~~~~~~~~~~~~~

For Slack: 
curl -X POST --data-urlencode 'payload={"channel": "#renderfarm", "username": "Render Chicken", "text": "Sample Text", "icon_emoji": ":chicken:"}' 

"""


def sendNotif(title, body):

	# URL incoming webhook for Mr X Tech Slack (protected)
	url = '*************************************************'

	payload = { 
		"channel": "#render-farm", 
		"username": "Render Chicken", 
		"text": "_*%s*_ - %s" % (title, body), 
		}


	r = requests.post(url, json=payload)


	if r.text == 'ok':
		return True
	else:
		return False



isDone = []
i = 0

while True:
	theNotif, i, isDone = main.initMain(i, isDone)

	if theNotif['msg'] != 'temp':
		print theNotif
		sendNotif(theNotif['msg'], theNotif['toPrint'])

	# changed to every min
	time.sleep(60)

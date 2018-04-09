import os

import tornado.gen
import tornado.web
import json

from common.web import requestsManager
from common.log import logUtils as log
from constants import exceptions
from common import generalUtils

MODULE_NAME = "clienterror"
REQUIRED_DATA = ["u", "osumode", "gamemode", "gametime", "audiotime", "culture", "b", "bc", "exception", "feedback", "stacktrace", "iltrace", "version", "exehash", "config"]
class handler(requestsManager.asyncRequestHandler):
	@tornado.web.asynchronous
	@tornado.gen.engine
	def asyncPost(self):
		try:
			if not requestsManager.checkArguments(self.request.arguments, REQUIRED_DATA):
				raise exceptions.invalidArgumentsException(MODULE_NAME)

			# Get a random error id
			found = False
			errorID = ""
			while not found:
				errorID = generalUtils.randomString(8)
				if not os.path.isfile(".data/clienterrors/{}.json".format(errorID)):
					found = True
			
			# Write error file to .data folder
			with open(".data/clienterrors/{}.json".format(errorID), "wb") as f:
				f.write(json.dumps({ k: self.get_argument(k).decode('utf-8') for k in self.request.arguments }))

			# Output
			log.info("New client-error from {}:{} ({})".format(self.get_argument("u"), self.get_argument("i"), errorID))

			self.write("")
		except exceptions.invalidArgumentsException:
			pass

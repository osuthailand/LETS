from lets import glob
from helpers import userHelper
from helpers import scoreHelper
from helpers import generalHelper
from constants import rankedStatuses
import beatmap
import os
from helpers import logHelper as log
if os.path.isfile("rippoppai.py"):
	import rippoppai

class score:
	def __init__(self, scoreID = None, rank = None):
		"""
		Initialize a (empty) score object.

		scoreID -- score ID, used to get score data from db. Optional.
		rank -- score rank. Optional
		"""
		self.scoreID = 0
		self.playerName = "nospe"
		self.score = 0
		self.maxCombo = 0
		self.c50 = 0
		self.c100 = 0
		self.c300 = 0
		self.cMiss = 0
		self.cKatu = 0
		self.cGeki = 0
		self.fullCombo = False
		self.mods = 0
		self.playerUserID = 0
		self.rank = 1	# can be empty string too
		self.date = 0
		self.hasReplay = 0

		self.fileMd5 = None
		self.passed = False
		self.playDateTime = 0
		self.gameMode = 0
		self.completed = 0

		self.accuracy = 0.00

		self.pp = 0.00

		self.oldPersonalBest = 0
		self.rankedScoreIncrease = 0

		if scoreID != None:
			self.setDataFromDB(scoreID, rank)

	def calculateAccuracy(self):
		"""
		Calculate and set accuracy for that score
		"""
		if self.gameMode == 0:
			# std
			totalPoints = self.c50*50+self.c100*100+self.c300*300
			totalHits = self.c300+self.c100+self.c50+self.cMiss
			if totalHits == 0:
				self.accuracy = 100
			else:
				self.accuracy = totalPoints/(totalHits*300)
		elif self.gameMode == 1:
			# taiko
			totalPoints = (self.c100*50)+(self.c300*100)
			totalHits = self.cMiss+self.c100+self.c300
			self.accuracy = totalPoints/(totalHits*100)
		elif self.gameMode == 2:
			# ctb
			fruits = self.c300+self.c100+self.c50
			totalFruits = fruits+self.cMiss+self.cKatu
			self.accuracy = fruits/totalFruits
		elif self.gameMode == 3:
			# mania
			totalPoints = self.c50*50+self.c100*100+self.cKatu*200+self.c300*300+self.cGeki*300
			totalHits = self.cMiss+self.c50+self.c100+self.c300+self.cGeki+self.cKatu
			self.accuracy = totalPoints / (totalHits * 300)
		else:
			# unknown gamemode
			self.accuracy = 0

	def setRank(self, rank):
		"""
		Force a score rank

		rank -- new score rank
		"""
		self.rank = rank

	def setDataFromDB(self, scoreID, rank = None):
		"""
		Set this object's score data from db
		Sets playerUserID too

		scoreID -- score ID
		rank -- rank in scoreboard. Optional.
		"""
		data = glob.db.fetch("SELECT *, users.username FROM scores LEFT JOIN users ON users.id = scores.userid WHERE scores.id = %s", [scoreID])
		if data != None:
			self.setDataFromDict(data, rank)
			self.playerUserID = userHelper.getID(self.playerName)

	def setDataFromDict(self, data, rank = None):
		"""
		Set this object's score data from dictionary
		Doesn't set playerUserID

		data -- score dictionarty
		rank -- rank in scoreboard. Optional.
		"""
		self.scoreID = data["id"]
		self.playerName = userHelper.getUsername(data["userid"])
		self.score = data["score"]
		self.maxCombo = data["max_combo"]
		self.c50 = data["50_count"]
		self.c100 = data["100_count"]
		self.c300 = data["300_count"]
		self.cMiss = data["misses_count"]
		self.cKatu = data["katus_count"]
		self.cGeki = data["gekis_count"]
		self.fullCombo = True if data["full_combo"] == 1 else False
		self.mods = data["mods"]
		self.rank = rank if rank != None else ""
		self.date = data["time"]
		self.fileMd5 = data["beatmap_md5"]
		self.completed = data["completed"]
		self.calculateAccuracy()

	def setDataFromScoreData(self, scoreData):
		"""
		Set this object's score data from scoreData list (submit modular)

		scoreData -- scoreData list
		"""
		if len(scoreData) >= 16:
			self.fileMd5 = scoreData[0]
			self.playerName = scoreData[1].strip()
			# %s%s%s = scoreData[2]
			self.c300 = int(scoreData[3])
			self.c100 = int(scoreData[4])
			self.c50 = int(scoreData[5])
			self.cGeki = int(scoreData[6])
			self.cKatu = int(scoreData[7])
			self.cMiss = int(scoreData[8])
			self.score = int(scoreData[9])
			self.maxCombo = int(scoreData[10])
			self.fullCombo = True if scoreData[11] == 'True' else False
			#self.rank = scoreData[12]
			self.mods = int(scoreData[13])
			self.passed = True if scoreData[14] == 'True' else False
			self.gameMode = int(scoreData[15])
			self.playDateTime = int(scoreData[16])
			self.calculateAccuracy()
			#osuVersion = scoreData[17]

			# Set completed status
			self.setCompletedStatus()


	def getData(self, username):
		"""Return score row relative to this score for getscores"""
		return "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|1\n".format(
			self.scoreID,
			self.playerName,
			self.score,
			self.maxCombo,
			self.c50,
			self.c100,
			self.c300,
			self.cMiss,
			self.cKatu,
			self.cGeki,
			self.fullCombo,
			self.mods,
			self.playerUserID,
			self.rank,
			generalHelper.osuDateToUNIXTimestamp(self.date))

	def setCompletedStatus(self):
		"""
		Set this score completed status and rankedScoreIncrease
		"""
		self.completed = 0
		if self.passed == True and scoreHelper.isRankable(self.mods):
			# Get userID
			userID = userHelper.getID(self.playerName)

			# Make sure we don't have another score identical to this one
			duplicate = glob.db.fetch("SELECT id FROM scores WHERE userid = %s AND beatmap_md5 = %s AND play_mode = %s AND score = %s", [userID, self.fileMd5, self.gameMode, self.score])
			if duplicate != None:
				# Found same score in db. Don't save this score.
				self.completed = -1
				return

			# No duplicates found.
			# Get right "completed" value
			personalBest = glob.db.fetch("SELECT id, score FROM scores WHERE userid = %s AND beatmap_md5 = %s AND play_mode = %s AND completed = 3", [userID, self.fileMd5, self.gameMode])
			if personalBest == None:
				# This is our first score on this map, so it's our best score
				self.completed = 3
				self.rankedScoreIncrease = self.score
				self.oldPersonalBest = 0
			else:
				# Compare personal best's score with current score
				if self.score > personalBest["score"]:
					# New best score
					self.completed = 3
					self.rankedScoreIncrease = self.score-personalBest["score"]
					self.oldPersonalBest = personalBest["id"]
				else:
					self.completed = 2
					self.rankedScoreIncrease = 0
					self.oldPersonalBest = 0

		log.debug("Completed status: {}".format(self.completed))

	def saveScoreInDB(self):
		"""
		Save this score in DB (if passed and mods are valid)
		"""
		# Add this score
		if self.completed >= 2:
			query = "INSERT INTO scores (id, beatmap_md5, userid, score, max_combo, full_combo, mods, 300_count, 100_count, 50_count, katus_count, gekis_count, misses_count, time, play_mode, completed, accuracy, pp) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
			self.scoreID = int(glob.db.execute(query, [self.fileMd5, userHelper.getID(self.playerName), self.score, self.maxCombo, 1 if self.fullCombo == True else 0, self.mods, self.c300, self.c100, self.c50, self.cKatu, self.cGeki, self.cMiss, self.playDateTime, self.gameMode, self.completed, self.accuracy*100, self.pp]))

			# Set old personal best to completed = 2
			if self.oldPersonalBest != 0:
				glob.db.execute("UPDATE scores SET completed = 2 WHERE id = %s", [self.oldPersonalBest])

	def calculatePP(self, b = None):
		"""
		Calculate this score's pp value if completed == 3
		"""
		if self.completed == 3:
			# Create beatmap object
			if b == None:
				b = beatmap.beatmap(self.fileMd5, 0)

			# Create an instance of the magic pp calculator and calculate pp
			if b.rankedStatus >= rankedStatuses.RANKED and b.rankedStatus != rankedStatuses.UNKNOWN:
				fo = rippoppai.oppai(b, self)
				self.pp = fo.pp
			else:
				self.pp = 0
		else:
			log.debug("Completed status is {}. PP calc for this score skipped.".format(self.completed))

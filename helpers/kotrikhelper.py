import hashlib
import re
from objects import glob


def verifyScoreData(scoreData, securityHash, bmk=None):
    #full nonHashedString = "chickenmcnuggets{}o15{}{}smustard{}{}uu{}{}{}{}{}{}{}Q{}{}{}{}{}{}"
    nonHashedString = "chickenmcnuggets{}o15{}{}smustard{}{}uu{}{}{}{}{}{}{}Q{}{}{}{}{}".format(
        int(scoreData[4])+int(scoreData[3]),
        int(scoreData[5]),
        int(scoreData[6]),
        int(scoreData[7]),
        int(scoreData[8]),
        scoreData[0].strip(),
        int(scoreData[10]),
        scoreData[11].strip(),
        scoreData[1].strip(),
        int(scoreData[9]),
        scoreData[12].strip(),
        int(scoreData[13]),
        scoreData[14].strip(),
        int(scoreData[15]),
        int(scoreData[17].strip()[:8]), # first 8 symbols, bcs its yyyymmdd\x14\x14\x14\x14\x14
        int(scoreData[16]),
        re.sub('[\x00-\x08\x0B-\x1F]', '', securityHash.strip())
    )

    hashedString = str(hashlib.md5(nonHashedString.encode()).hexdigest())
    if hashedString == scoreData[2]:
        return True
    
    return False

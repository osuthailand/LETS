import hashlib
import re
from objects import glob


def verifyScoreData(scoreData, securityHash, sbk=None):
    # Full nonHashedString
    # Taken from osu! v20200519.1
    # chickenmcnuggets{0}o15{1}{2}smustard{3}{4}uu{5}{6}{7}{8}{9}{10}{11}Q{12}{13}{15}{14:yyMMddHHmmss}{16}{17}
    # {0} = Count100 + Count300
    # {1} = Count50
    # {2} = CountGeki
    # {3} = CountKatu
    # {4} = CountMiss
    # {5} = FileChecksum
    # {6} = MaxCombo
    # {7} = Perfect
    # {8} = PlayerName
    # {9} = TotalScore
    # {10} = Rank
    # {11} = (int)(Mods)EnabledMods
    # {12} = Pass
    # {13} = (int)PlayMode
    # {14} = Date.ToUniversalTime()
    # {15} = General.VERSION
    # {16} = GameBase.ClientHash
    # {17} = Beatmap.StoryboardHash
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
        re.sub('[\x00-\x08\x0B-\x1F]', '', securityHash.strip()),
        sbk
    )

    hashedString = str(hashlib.md5(nonHashedString.encode()).hexdigest())
    if hashedString == scoreData[2]:
        return True
    
    return False

from model import *
from view import *
from controller import *

import datetime
rules = GameRules(PLACEMENT=PlacementRules.AUTOMATIC_PLACEMENT,
                  MAP=MapRules.ANTIQUITY,
                  RECRUITMENT=RecruitmentRules.FIXED,
                  FORTIFICATION=FortifyRules.ADJACENT, 
                  WIN_CONDITION=WinConditionRules.HUNDRED_PERCENT
                 )

test_metadata = GameMetadata(1, 
                        datetime.time.max, 
                        GameMode.LOCAL_PLAY, 
                        players=[Player(1, "Andrew", "red"), Player(2, "Bob", "green")], 
                        rules=rules
                        )

game = Game.create(test_metadata)
view = ConsoleView(game)
controller = ConsoleController(game)
game.start()

while True: 
    inp = input()
    controller.parse_request(inp)

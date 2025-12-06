from model import *

class ConsoleController:
    def __init__(self, game: Game):
        self.game = game

        self.command_lookup = {"continents" : ViewContinentsCommand,
                               "territories" : ViewTerritoriesCommand,
                               "cards": ViewCardsCommand,
                               "save": SaveCommand,
                               "load": LoadCommand,
                               "next": NextTurnCommand,
                               "close": CloseGameCommand,
                               "trade": TradeSetCommand,
                               "place": PlaceUnitCommand,
                               "transfer": FortifyTerritoryCommand,
                               "focus": FocusOffensiveCommand,
                               "cancel": CancelFocusOffensiveCommand,
                               "manual": AttackManualCommand,
                               "simulate": AttackSimulateCommand,
                               "attacker_dice": ChangeAttackerDiceCommand,
                               "defender_dice": ChangeDefenderDiceCommand,
                               "loss_threshold": ChangeLossThresholdCommand
                              }
        
    def parse_request(self, request: str) -> None:
        try:
            request = request.strip().split(" ")
            command_type = self.command_lookup[request[0]]

            parameters = []
            for parameter in request[1:]:
                if parameter.strip("-").isdigit():
                    parameters.append(int(parameter))
                else:
                    parameters.append(self.game.get_territory_from_id(parameter))
            command = command_type(*parameters)
            self.game.execute(command)

        except Exception as e:
            print(e)

    def create_metadata(self) -> GameMetadata:
        while True:
            try:
                while True:
                    gamemode = input("Which gamemode are you playing? ")
                    if gamemode in GameMode:
                        break
                    else:
                        print("Input LOCAL_PLAY, TRAINING, or SIMULATION!")
                    num_players = int(input("Input how many players there will be from 0 to 6: "))
                    
                




            except Exception as e:
                print(e)

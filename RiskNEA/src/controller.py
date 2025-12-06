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
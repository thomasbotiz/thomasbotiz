from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
import sys

from ..utils import Command, ExplicitEvent, OffensiveFront, BattleStatus, ManualBattleResult, SimulateBattleResult
from ..main.config import PlacementConfig, RecruitmentConfig, AttackConfig
from ..main.rules import PlacementRules, RecruitmentRules, FortifyRules

if TYPE_CHECKING:
    from ..main.game import Game
    from .board.board import Territory, Continent
    from .player.player import Player
    from .deck.deck import Card

class SaveCommand(Command):
    def __init__(self, file_name: str):
        """
        A command to save the game to /saves

        Parameters
        ----------
        filename : str
            The name of the file being saved.
        
        Notes
        -----
        Should overwrite the file if any is specified
        """
        self.file_name = file_name

    def _validate(self, game: Game) -> str:
        """
        Checks if the command is valid to call or not

        Parameters
        ----------
        game : Game
            The game being edited

        Notes
        -----
        Meta Commands should be validated by State, rather than
        the command itself. This is because the validation need
        to polymorph depending on what State it is called in.
        """
        return ""
    
    def execute(self, game: Game):
        """
        Saves the game 

        Parameters
        ----------
        game : Game
            The game being edited
        """
        error = self._validate(game)

        if not error:
            game.save_game(self.file_name)
        
        return SaveGameEvent(self.file_name)


@dataclass
class SaveGameEvent(ExplicitEvent):
    """
    Event emitted when a player saves the game

    Attributes
    -------
    file_name : str
        The name of the file that was just saved
    """
    file_name: str


class LoadCommand(Command):
    def __init__(self, file_name: str):
        """
        A command to set the current game
        to the one in the specified file

        Parameters
        ----------
        filename : str
            The name of the file being saved.

        Notes
        -----
        Should overwrite the file if present
        """
        self.file_name = file_name

    def _validate(self) -> str:
        """
        Checks if the command is valid to call or not

        Notes
        -----
        Normal Commands should be validated by State, rather than
        the command itself. This is because the validation need
        to polymorph depending on what State it is called in.
        """
        return ""
    
    def execute(self, game: Game) -> LoadGameEvent:
        """
        Sets the new game to inherit the properties given
        by the file

        Parameters
        ----------
        game : Game
            The game being appended to
        
        Returns
        -------
        LoadGameEvent
            The results of loading a new game

        Notes
        -----
        Must create a new game and manually replace each
        game attribute individually, assigning it directly
        just creates a new local variable.
        """

        new_game = Game.load_game(self.file_name)
        game.metadata = new_game.metadata
        game.data = new_game.data
        game.stats = new_game.stats

        return SaveGameEvent(self.file_name)


@dataclass
class LoadGameEvent(ExplicitEvent):
    """
    Event emitted when a player saves the game

    Attributes
    -------
    file_name : str
        The name of the file that was just saved
    """
    file_name: str


class NextTurnCommand(Command):
    def __init__(self):
        """
        A command to signal a request to move to 
        the next game state
        """
    
    def _validate(self, game: Game) -> str:
        """
        Checks if the command is valid to call or not

        Parameters
        ----------
        game : Game
            The game instance being executed on

        Returns
        str
            The accompanying error message 
            
        Notes
        -----
        See each accompanying state for when the command
        is valid. 
        
        This is a dummy so that an error is 
        not returned by State when calling.
        """
        error = ""
        return error
        
    def execute(self, game: Game) -> NextTurnCommand:
        """
        Signals to Game to switch State

        Parameters
        ----------
        game : Game
            The game instance being executed on

        Returns
        -------
        NextTurnEvent
            A request to switch to the next state
        """
        error = self._validate(game)

        if not error:
            return NextTurnEvent(error)

@dataclass
class NextTurnEvent(ExplicitEvent):
    """
    Event emitted when a player proceeds to the next turn

    Attributes
    ----------
    str
        The accompanying error message
        
    Notes
    -----
    Naming convention breaks slightly so that it is clear this event 
    is as a result of the player inputting the request, rather than
    actually executing it.
    """
    error: str

@dataclass 
class PlaceUnitCommand(Command):
    def __init__(self, territory: Territory, units_placed: int):
        """
        Command called when a player attempts to place a unit on a
        territory using the player's reserves in any phase

        Attributes
        ----------
        territory : Territory
            The territory being placed on
        units_placed : int
            The number of units placed
        
        Notes
        -----
        This will be called for all the states, so it should 
        have very minimal logic itself. 

        The alternative to this would be having separate commands
        for each phase, which would be unintuitive for an end user.
        """
        self.territory = territory
        self.units_placed = units_placed

    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to place a unit 
        on that territory.
        
        Notes
        -----
        No matter the phase, there are some rules
        in which PlaceUnitCommand should not validate.

        The territory must be owned by the player, and
        the units placed must not be greater than the units
        the player has left.
        """
        error = ""
        if self.units_placed <= 0:
            error += "Invalid integer inputted!\n"

        if self.units_placed > game.current_player.units_to_place:
            error += "Player does not have that many units left!\n"
        
        if game.board.all_territories_claimed: 
            if self.territory.owner != game.current_player:
                error += "Cannot place on another player's territory!\n"
        return error.strip()

    def execute(self, game: Game) -> PlaceUnitEvent:
        """
        Places units on that territory if it 
        is valid in both State and Command validation
        
        Parameters
        ----------
        game : Game
            The game instance being executed to 

        Notes
        -----
        Actual execution is offloaded to the State. 
        """
        error = self._validate(game)

        if not error:
            self.territory.units += self.units_placed
            game.current_player.units_to_place -= self.units_placed
            if not self.territory.owner:
                self.territory.owner = game.current_player
        
        return PlaceUnitEvent(error,
                              game.current_player,
                              self.territory,
                              self.units_placed
                             )

@dataclass
class PlaceUnitEvent(ExplicitEvent):
    """
    An event emitted when a player calls PlaceUnitCommand

    Attributes
    ----------
    error : str
        The error message that came with the failed command
    player : Player
        The player who issued the recruitment command
    territory : Territory
        The territory that a unit was placed on
    units_placed : int 
        The number of units placed
    """
    error: str
    player: Player
    territory: Territory
    units_placed: int


class CloseGameCommand(Command):
    def __init__(self):
        """
        A command to stop the program
        """

    def _validate(self, game: Game):
        error = ""
        return error.strip()
    
    def execute(self, game):
        error = self._validate(game)
        if not error: 
            sys.exit()

        return CloseGameEvent(error=error)
    

@dataclass
class CloseGameEvent(ExplicitEvent):
    """
    An event emitted when the game is closed
    """
    error: str

class ViewContinentsCommand(Command):
    def __init__(self):
        """
        A command to view all continents and their 
        properties
        """
    
    def _validate(self, game: Game):
        """
        Checks when it is legal to view all the 
        continents

        Parameters
        ----------
        game : Game
            The game instance being validated on

        Notes
        -----
        ViewContinents should always validate
        because it is a query method.
        """
    
    def execute(self, game: Game) -> ViewContinentsEvent:
        """
        Outputs information about all the 
        game continents

        Parameters
        ----------
        game : Game
            The game instance being validated on
        
        Returns
        ViewContinentsEvent
            A representation of all the game continents
        """
        error = self._validate(game)

        if not error:
            return ViewContinentsEvent(error, game.board.continents)

@dataclass
class ViewContinentsEvent(ExplicitEvent):
    """
    Event emitted when a player queries to see
    all the continents

    Attributes
    ----------
    error : str
        The error message that came with the command
    continents : list[Continent]
        All continents in the game
    """
    error: str
    continents: list[Continent]


class ViewTerritoriesCommand(Command):
    def __init__(self):
        """
        A command to view all territories and their 
        properties
        """
    
    def _validate(self, game: Game):
        """
        Checks when it is legal to view all the 
        continents

        Parameters
        ----------
        game : Game
            The game instance being validated on

        Notes
        -----
        ViewTerritories should always validate
        because it is a query method.
        """
    
    def execute(self, game: Game) -> ViewTerritoriesEvent:
        """
        Outputs information about all the 
        game continents

        Parameters
        ----------
        game : Game
            The game instance being validated on
        
        Returns
        ViewTerritoriesEvent
            A representation of all the game continents
        """
        error = self._validate(game)

        if not error:
            return ViewTerritoriesEvent(error, game.board.territories)


@dataclass
class ViewTerritoriesEvent(ExplicitEvent):
    """
    Event emitted when a player queries to see
    all the continents

    Attributes
    ----------
    error : str
        The error message that came with the command
    territories : list[Territory]
        All continents in the game
    """
    error : str
    territories : list[Territory]
    
class ViewCardsCommand(Command):
    def __init__(self):
        """
        A command to view all the current player's cards and their 
        properties
        """
    
    def _validate(self, game: Game):
        """
        Checks when it is legal to view all the 
        cards

        Parameters
        ----------
        game : Game
            The game instance being validated on

        Notes
        -----
        ViewCards should always validate
        because it is a query method.
        """
    
    def execute(self, game: Game) -> ViewCardsEvent:
        """
        Outputs information about all the 
        game continents

        Parameters
        ----------
        game : Game
            The game instance being validated on
        
        Returns
        ViewContinentsEvent
            A representation of all the game continents
        """
        error = self._validate(game)

        if not error:
            return ViewCardsEvent(error, game.current_player, game.current_player.cards)


@dataclass
class ViewCardsEvent(ExplicitEvent):
    """
    Event emitted when a player queries to see
    all the continents

    Attributes
    ----------
    error : str
        The error message that came with the command
    cards : list[Card]
        All cards in the game
    """
    error: str
    player: Player
    cards: list[Card]

    
class TradeSetCommand(Command):
    def __init__(self, cards: list[Card]):
        """
        A command to trade in a set of cards
        
        Attributes
        ----------
        Cards : List[Card]
            The cards being traded in by the player
        """
        self.cards = cards

    def execute(self, game: Game) -> TradeSetEvent:
        """
        Add the corresponding number of units to a player's
        unplaced_units if the cards are valid 

        Returns
        -------
        TradeSetEvent
            Data representing the change made to Game
        
        error : str
            Accompanying error message if success is False
        player : Player
            The player who issued the command to trade in the set
        set_traded_in : list[Card]
            The set that was just traded in 
        
        Notes
        -----
        Should use Games interface to calculate how many units
        the set is worth 
        """
        error = self._validate(game)
        units_received = game.get_set_value(self.cards)

        if not error:
            game.current_player.units_to_place += units_received
            game.current_player.cards = list(set(game.current_player.cards) - set(self.cards))
            game.current_player.stats.total_units_recruited += units_received
            game.stats.traded_in_sets += 1
            game.stats.units_recruited += units_received
        
        return TradeSetEvent(error = error,
                            player = game.current_player,
                            cards = self.cards,
                            units_received=units_received
                            )

    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to trade in the set of cards

        Parameters
        ----------
        game : Game
            The game being executed on
        
        Returns
        -------
        str
            The accompanying error message(None assumes command is valid)
        

        Notes
        -----
        TradeSetAttackCommand would fully validate if: 

        There are three cards in Cards.

            AND 

        The current player owns all three of those cards.

            AND 

        The cards combine to form a valid set.
        """
        error = ""

        if len(self.cards) != RecruitmentConfig.CARDS_IN_SET:
            error += "Not possible to trade this number of cards!"

        for card in self.cards:
            if card not in game.current_player.cards:
                error += "You must own the traded in cards!"
                break

        units_received = game.get_set_value(self.cards)
        if not units_received:
            error += "Set must be of a valid combination of cards!"
        return error.strip()

@dataclass
class TradeSetEvent(ExplicitEvent):
    """
    An event emitted after AttackTradeSetCommand is called
    
    Attributes
    ----------
    error : str
        The error message that came with the failed command(None assumes success)
    player : Player
        The player who issued the recruitment command
    cards : list[Card]
        The cards that were traded in
    units_received : int
        The units received at the start of the turn/from trading in the set
    """
    error: str
    player: Player
    cards: list[Card]
    units_received: int


class FortifyTerritoryCommand(Command):
    def __init__(self, territory_from: Territory, territory_to: Territory, units_transferred: int):
        """
        A command to transfer units from one territory to the other
        
        Attributes
        ----------
        territory_from : Territory
            The territory having units transferred from
        territory_to : Territory
            The territory being fortified
        units_transferred : int
            The number of units transferred from `territory_from` to `territory_to`
        """
        self.territory_from = territory_from
        self.territory_to = territory_to
        self.units_transferred = units_transferred
        
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to fortify
        the specified territory

        Parameters
        ----------
        game : Game
            The instance of game being executed on

        Returns
        -------
        str
            The accompanying error message(None assumes valid)
        
        Notes
        -----
        FortifyTerritoryCommand should validate if:

        territory_from is owned by the current turn player

            AND 

        territory_to is owned by the current turn player

            AND
        
        the number of units on `territory_from` is greater than
        `units_transferred` (the fortifying territory must be left
        with one or more units)

        The territories are directly connected and contiguous rules 
        are enabled

        OR the territories are indirectly connected 
        and adjacent rules are enabled
        """
        error = ""
        friendly_territories = game.board.get_friendly_territories(game.current_player)
        if self.units_transferred <= 0:
            error += "Invalid number specified!\n"
        if self.territory_from not in friendly_territories:
            error += "Transferring territory is not owned by the player!\n"
        if self.territory_to not in friendly_territories:
            error += "Territory transferring to is not owned by the player!\n"
        if self.units_transferred >= self.territory_from.units:
            error += "The defending territory must be left with at least one unit!\n"

        if game.rules.FORTIFICATION == FortifyRules.ADJACENT:
            if not game.board.has_adjacency(self.territory_from, self.territory_to):
                error += "The territories must be adjacent to fortify!\n"

        elif game.rules.FORTIFICATION == FortifyRules.CONTIGUOUS:
            if self.territory_from not in self.territory_to.connected_territories:
                error += "The territories must be directly connected to fortify!\n"
        
        return error.strip()

    def execute(self, game: Game) -> FortifyTerritoryEvent:
        """
        Transfers units from one territory to the other 
        if the units and territories are valid

        Returns
        -------
        FortifyTerritoryEvent
            Data representing the changes made to `Game` by FortifyTerritoryCommand
        
        error : str
            The accompanying error message from _validate()
        player : Player
            The player who issued the command 
        territory_from : Territory
            The territory having units transferred from
        territory_to : Territory
            The territory that is fortified
        units_transferred : int
            The number of units transferred
        """
        error = self._validate(game)

        if not error:
            self.territory_from.units -= self.units_transferred
            self.territory_to.units += self.units_transferred
        
        return FortifyTerritoryEvent(error = error,
                                     player = game.current_player,
                                     territory_from = self.territory_from,
                                     territory_to = self.territory_to,
                                     units_transferred = self.units_transferred
                                     )
    
@dataclass
class FortifyTerritoryEvent(ExplicitEvent):
    """
    Event emitted when a territory is fortified

    Attributes
    ----------
    error : str
        The accompanying error message from _validate()
    player : Player
        The player who issued the command 
    territory_from : Territory
        The territory having units transferred from
    territory_to : Territory
        The territory that is fortified 
    units_transferred : int
        The number of units transferred
    """
    error: str
    player: Player
    territory_from: Territory
    territory_to: Territory
    units_transferred: int


class FocusOffensiveCommand(Command):
    def __init__(self, territory_from: Territory, territory_to: Territory):
        """
        A command to set the focus of attack between two territories

        Parameters
        ----------
        territory_from : Territory
            The territory the attack is commenced from
        territory_to : Territory
            The defending territory being captured 
        """
        self.territory_from = territory_from
        self.territory_to = territory_to
    
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to create a front between the desired territories 

        Parameters
        ----------
        game : Game 
            The instance of Game being executed on

        Returns
        -------
        str 
            The accompanying error message(None assumes valid)

        Notes
        -----
        FocusOffensiveCommand should validate if:

        territory_from is owned by the current turn player and has more
        than one unit

            AND

        territory_to is owned by an opponent player and is contiguous to 
        territory_from
        """
        error = ""
        if self.territory_from.units < 2:
            error += "Attacking territory must have at least 2 units!\n"
        if self.territory_from not in self.territory_to.connected_territories:
            error += "Attacking territory must be connected to the defending territory!\n"
        if  self.territory_from not in game.board.get_friendly_territories(game.current_player):
            error += "You must own the attacking territory!\n"
        if self.territory_from.owner == self.territory_to.owner:
            error += "Cannot attack a friendly territory!\n"
        return error.strip()
        
    def execute(self, game: Game) -> FocusOffensiveEvent:
        """
        Sets the active attack of State between the desired territories

        Attributes
        ----------
        game : Game
            The instance of Game being executed on 
        
        Returns
        -------
        FocusOffensiveEvent
            Data on what was changed in `Game`  

        Notes
        -----
        When creating OffensiveFront object, should set the attacking dice
        and defending dice to max possible, set loss_threshold
        to 0. Do not emit a separate event to relay this. 
        """
        error = self._validate(game)
        if not error:
            attacker_dice = min(AttackConfig.MAX_ATTACKER_DICE, self.territory_from.units - 1)
            defender_dice = min(AttackConfig.MAX_DEFENDER_DICE, self.territory_to.units)
            loss_threshold = 0
            front = OffensiveFront(self.territory_from,
                                            self.territory_to,
                                            attacker_dice,
                                            defender_dice,
                                            loss_threshold,
                                            status = BattleStatus.ONGOING
                                )
        else:
            front = None

        return FocusOffensiveEvent(error=error, 
                                   front=front)


@dataclass
class FocusOffensiveEvent(ExplicitEvent):
    """
    An event emitted when the player focuses on a front 

    Attributes
    ----------
    error : str
        The accompanying error message from _validate()
    offensive_front : OffensiveFront
        The front storing data about the currently
        focused on battle.    
    
    Defaults to erroneous data in case of an error.
    """
    error : str
    front : Optional[OffensiveFront] = None


class CancelFocusOffensiveCommand(Command):
    def __init__(self):
        """
        A command to forget the front being focused on
        """
    
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to cancel the front in State 

        Parameters
        ----------
        game : Game 
            The instance of Game being executed on

        Returns
        -------
        str 
            The accompanying error message(None assumes valid)

        Notes
        -----
        CancelFocusOffensiveCommand should validate if:

        front is defined as anything except None 
        """
        error = ""
        return error.strip()
        
    
    def execute(self, game: Game) -> CancelFocusOffensiveEvent:
        """
        Sets front in State to None 

        Attributes
        ----------
        game : Game
            The instance of Game being executed on 
        
        Returns
        -------
        CancelFocusOffensiveEvent
            Data on what was changed in `Game`  

        Notes
        -----
        Modifies State's front by interacting with the interface, overwriting 
        if necessary.
        """
        error = self._validate(game)
        return CancelFocusOffensiveEvent(error)


@dataclass
class CancelFocusOffensiveEvent(ExplicitEvent):
    """
    An event emitted when a player cancels a front 

    Attributes
    ----------
    error : str
        The accompanying error message from _validate()
    """
    error: str


class AttackManualCommand(Command):
    def __init__(self):
        """
        A command to simulate one round of combat in front
        """
    
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to call the command
        
        Attributes
        ----------
        game : Game
            The instance of Game being executed on
        
        Returns
        -------
        str
            The accompanying error message(None assumes valid)

        Notes
        -----
        AttackManualCommand should validate if: 

        front is defined in state

        Note that all validation occurs when selecting the front
        in the first place, so this should always validate.
        """
        error = ""
        return error.strip()

    def execute(self, game: Game) -> AttackManualEvent:
        """
        Simulates a round of battle between the territories
        if valid 

        Parameters
        ----------
        game : Game
            The instance of Game being executed on 
        
        Returns
        -------
        AttackManualEvent
            Data on what was changed in `Game`  

        Notes
        -----
        Modifies State's front by interacting with the interface, overwriting 
        if necessary.
        """
        error = self._validate(game)

        if not error:
            result = game.state.front.manual_attack()

            return AttackManualEvent(error = error,
                                     attacker_rolls = result.attacker_rolls,
                                     defender_rolls = result.defender_rolls,
                                     attacker_units_lost= result.attacker_units_lost,
                                     defender_units_lost= result.defender_units_lost,
                                     territory_from = result.front.territory_from,
                                     territory_to = result.front.territory_to
                                    )

        else:
            return AttackManualEvent(error = error)
        
@dataclass
class AttackManualEvent(ExplicitEvent):
    """
    An event emitted after a manual battle command is executed

    Attributes
    ----------
    error : str
            The accompanying error message from _validate()
    attacker_rolls : List[int]
        The values of the attacker's dice sorted in descending order
    defender_rolls : List[int]
        The values of the defender's dice sorted in descending order
    attacker_units_lost : int 
        The number of units removed from the attacking territory
    defender_units_lost : int 
        The number of units removed from the defending territory 
    territory_from : Territory
        The name of the attacking territory
    territory_to : Territory
        The name of the defending territory 

    Defaults to erroneous data in case of an error
    """
    error: str
    territory_from : Optional[Territory] 
    territory_to : Optional[Territory]
    attacker_rolls: list[int]
    defender_rolls: list[int]
    attacker_units_lost: int
    defender_units_lost: int


class AttackSimulateCommand(Command):
    def __init__(self):
        """
        A command to simulate battle in the front 
        until the attack is successful, repelled
        or meets the loss threshold 
        """
    
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to call the command
        
        Attributes
        ----------
        game : Game
            The instance of Game being executed on
        
        Returns
        -------
        str
            The accompanying error message(None assumes valid)

        Notes
        -----
        AttackSimulateCommand should validate if: 

        front is defined in state

        Note that all validation occurs when selecting the front
        in the first place.
        """
        error = ""
        return error.strip()

    def execute(self, game: Game) -> AttackSimulateEvent:
        """
        Simulates battle between the territories
        if valid until the attack is repelled,
        successful or meets the loss threshold

        Attributes
        ----------
        game : Game
            The instance of Game being executed on 
        
        Returns
        -------
        AttackSimulateEvent
            Data on what was changed in `Game`  

        Notes
        -----
        Should stop when front's loss threshold is met, 
        the defending territory has zero units left, the attacking
        territory has 1 unit left, or the attacking territory
        has less than or equal to the loss threshold 

        Should calculate the winner of the battle immediately,
        not create a list of arrays. Could be changed in the 
        future. 
        """ 
        error = self._validate(game)

        if not error:
            result = game.state.front.simulate_attack()

            return AttackSimulateEvent(error = error,
                                       total_attacker_units_lost = result.total_attacker_units_lost,
                                       total_defender_units_lost = result.total_defender_units_lost,
                                       territory_from = result.front.territory_from,
                                       territory_to = result.front.territory_to
                                       )
        else:
            return AttackSimulateEvent(error = error)

@dataclass
class AttackSimulateEvent(ExplicitEvent):
    """
    An event emitted after a manual battle command is executed

    Attributes
    ----------
    error : str
        The accompanying error message from _validate()
    territory_from : Territory
        The territory the attack is commenced from
    territory_to : Territory
        The territory under attack 
    attacker_units_lost : int
        The number of units removed from the attacking territory
    defender_units_lost : int 
        The number of units removed from the defending territory 

    Notes
    -----
    Information about which player won is already
    handled by an Implicit Event.

    Defaults to erroneous data in case of an error.
    """
    error: str
    territory_from: Optional[Territory] = None 
    territory_to: Optional[Territory] = None 
    total_attacker_units_lost: int = 0
    total_defender_units_lost: int = 0
    

class ChangeAttackerDiceCommand(Command):
    def __init__(self, count: int):
        """
        A command to change the number
        of dice the attacker uses in the front
        
        Attributes
        ----------
        count : int
            The new number of dice for the attacker
        """
        self.count = count
    
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to call the command
        
        Parameters
        ----------
        game : Game
            The instance of Game being executed on
        
        Returns
        -------
        str
            The accompanying error message(None assumes valid)

        Notes
        -----
        AttackChangeAttackerDice should validate if: 

        front is defined in state

            AND

        count is within a valid range

        Notes
        -----
        The valid range of count should factor in how many 
        units the attacking player has.

        Should also display the maximum number of dice allowed
        in the error message if applicable
        """
        error = ""

        if not game.state.front:
            error += "Focus on a front first!\n"
        elif self.count > game.state.front.max_attacker_dice:
            error += f"Can only use {game.state.front.max_attacker_dice}!\n"
        elif self.count <= 0:
            error += "Invalid dice specified!\n"
        
        return error.strip()
    
    def execute(self, game: Game) -> ChangeAttackerDiceEvent:
        """
        Changes the number of dice the attacking player is using

        Parameters
        ----------
        game : Game
            The instance of Game being executed on
        
        Returns
        -------
        AttackChangeAttackerDiceEvent
            Data on what was changed in `Game`
        """
        error = self._validate(game)
        if not error:
            game.state.front.attacker_dice = self.count
            return ChangeAttackerDiceEvent(error = error,
                                           player = game.current_player,
                                           count = self.count)
        else:
            return ChangeAttackerDiceEvent(error = error)
   
        
@dataclass
class ChangeAttackerDiceEvent(ExplicitEvent): 
    """
    An event emitted after the attacker changes their dice count
    
    Attributes
    ----------
    error : str
            The accompanying error message from _validate()
    player : Player
        The name of the player changing their dice
    count : int
        The new number of dice being used 
    """
    error: str
    player: Optional[Player]
    count: int 

class ChangeDefenderDiceCommand(Command):
    def __init__(self, count: int):
        """
        A command to change the number
        of dice thed defender uses in the front
        
        Attributes
        ----------
        count : int
            The new number of dice for the defender
        """
        self.count = count
    
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to call the command
        
        Parameters
        ----------
        game : Game
            The instance of Game being executed on
        
        Returns
        -------
        str
            The accompanying error message(None assumes valid)

        Notes
        -----
        AttackChangeDefenderDiceCommand should validate if: 

        front is defined in state

            AND

        count is within a valid range

        Notes
        -----
        The valid range of count should factor in how many 
        units the attacking player has.

        Should also display the maximum number of dice allowed
        in the error message if applicable
        """
        error = ""

        if not game.state.front:
            error += "Focus on a front first!\n"
        
        elif self.count > game.state.front.max_defender_dice:
            error += f"The max number of dice allowed is {game.state.front.max_defender_dice}!\n"
        
        elif self.count <= 0:
            error += "Invalid dice specified!\n"
        
        return error.strip()
    
    def execute(self, game: Game) -> ChangeDefenderDiceEvent:
        """
        Changes the number of dice the defending player is using

        Parameters
        ----------
        game : Game
            The instance of Game being executed on
        
        Returns
        -------
        AttackChangeDefenderDiceEvent
            Data on what was changed in `Game`
        """
        error = self._validate(game)
        
        if not error:
            game.state.front.defender_dice = self.count

            return ChangeDefenderDiceEvent(error = error,
                                           count = self.count,
                                           player = game.current_player)

        else:
            return ChangeDefenderDiceEvent(error = error)

@dataclass
class ChangeDefenderDiceEvent(ExplicitEvent): 
    """
    An event emitted after the defender changes their dice count
    
    Attributes
    ----------
    error : str
            The accompanying error message from _validate()
    player : str
        The player changing their dice
    count : int
        The new number of dice being used 

    Defaults to erroneous data in case of an error
    """
    error: str
    player: Optional[Player]
    count: int 

class ChangeLossThresholdCommand(Command):
    def __init__(self, loss_threshold: int):
        """
        A command to change the loss threshold of the attacker
        
        Parameters
        ----------
        new_threshold : int   
            The new attack threshold before stopping simulation
        """
        self.loss_threshold = loss_threshold
    
    def _validate(self, game: Game) -> str:
        """
        Checks if it is legal to call the command
        
        Attributes
        ----------
        game : Game
            The instance of Game being executed on
        
        Returns
        -------
        str
            The accompanying error message("" assumes valid)

        Notes
        -----
        AttackChangeLossThresholdCommand should validate if: 

        front is defined in state

            AND
        
        loss_threshold is less than or equal to the number of 
        attacking units
        """
        error = ""
        if not game.state.front:
            error += "Focus on a front first!\n"

        elif self.loss_threshold >= game.state.front.territory_from.units - 1 :
            error += "You do not have enough units!\n"
        
        elif self.loss_threshold < 0:
            error += "Invalid number!\n"
        
        return error.strip()
    
    def execute(self, game: Game) -> ChangeLossThresholdEvent:
        """
        Changes the loss threshold of the current
        front for simulated battles

        Attributes
        ----------
        game : Game
            The instance of Game being executed on 
        
        Returns
        -------
        AttackChangeLossThresholdEvent 
            Data on what was changed in `Game`  

        Notes
        -----
        Should stop when front's loss threshold is met, 
        the defending territory has zero units left, the attacking
        territory has 1 unit left, or the attacking territory
        has less than or equal to the loss threshold 

        Should calculate the winner of the battle immediately,
        not create a list of arrays. Could be changed in the 
        future. 
        """
        error = self._validate(game)

        if not error:
            game.state.front.loss_threshold = self.loss_threshold
        
            return ChangeLossThresholdEvent(error = error,
                                            player_from = game.state.front.territory_from.owner,
                                            loss_threshold = self.loss_threshold
                                            )
        else:
            return ChangeLossThresholdEvent(error = error)


@dataclass
class ChangeLossThresholdEvent(ExplicitEvent):
    """
    An event emitted after the loss threshold is changed

    Attributes
    ----------
    error : str
        The accompanying error message from _validate()
    player : Player
        The player commencing the attack
    loss_threshold : int
        The new loss threshold 

    Defaults to erroneous data for errors.
    """
    error: str
    player: Optional[Player]
    loss_threshold: int

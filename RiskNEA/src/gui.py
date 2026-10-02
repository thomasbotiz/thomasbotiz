from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
import tkinter
import sys

from model import *

if TYPE_CHECKING:
    from ai_controller import AIController

class LocalPlayGUI(tkinter.Tk):
    def __init__(self, game: Game, ai_controllers: list[AIController]):
        super().__init__()
        self.ai_controllers = ai_controllers
        self.geometry("1080x720")
        self.title("Risk")
        self.resizable(False, False)

        self.game = game
        self.service = MapStateService(self)
        self.game.event_bus.subscribe(LoadGameEvent, self.on_load)
        self.game.event_bus.subscribe(SaveGameEvent, self.on_save)
        self.game.event_bus.subscribe(NextTurnEvent, self.on_next_turn)
        self.game.event_bus.subscribe(PlacementPhaseStartedEvent, self.on_placement_phase_started)
        self.game.event_bus.subscribe(PlacementPhaseFortifyingEvent, self.on_placement_phase_fortifying)
        self.game.event_bus.subscribe(EndPhaseStartedEvent, self.on_end_phase_started)
        self.game.event_bus.subscribe(ViewTerritoriesEvent, self.on_territory_view_toggled)
        self.game.event_bus.subscribe(ViewContinentsEvent, self.on_continent_view_toggled)
        self.game.event_bus.subscribe(ViewCardsEvent, self.on_card_view_toggled)

        self.game.event_bus.subscribe(PlaceUnitEvent, self.on_unit_placed)
        self.game.event_bus.subscribe(RecruitmentPhaseStartedEvent, self.on_recruitment_phase_started)
        self.game.event_bus.subscribe(ForcedCardTradeEvent, self.on_forced_card_trade)
        self.game.event_bus.subscribe(TradeSetEvent, self.on_trade_set)
        self.game.event_bus.subscribe(AttackPhaseStartedEvent, self.on_attack_phase_started)
        self.game.event_bus.subscribe(NoAttacksLeftEvent, self.on_no_attacks_left)
        self.game.event_bus.subscribe(CardReceivedEvent, self.on_card_received)
        self.game.event_bus.subscribe(AttackSuccessfulEvent, self.on_attack_successful)
        self.game.event_bus.subscribe(ExpectingTransferEvent, self.on_expecting_transfer)
        self.game.event_bus.subscribe(AttackRepelledEvent, self.on_attack_repelled)
        self.game.event_bus.subscribe(ContinentCapturedEvent, self.on_continent_captured)
        self.game.event_bus.subscribe(PlayerEliminatedEvent, self.on_player_eliminated)
        self.game.event_bus.subscribe(CardsTransferredEvent, self.on_cards_transferred)
        self.game.event_bus.subscribe(RequiredTradeEvent, self.on_forced_card_trade)
        self.game.event_bus.subscribe(FocusOffensiveEvent, self.on_focus_offensive)
        self.game.event_bus.subscribe(CancelFocusOffensiveEvent, self.on_cancel_offensive)
        self.game.event_bus.subscribe(AttackManualEvent, self.on_manual_attack)
        self.game.event_bus.subscribe(AttackSimulateEvent, self.on_simulate_attack)
        self.game.event_bus.subscribe(ChangeAttackerDiceEvent, self.on_change_attacker_dice)
        self.game.event_bus.subscribe(ChangeDefenderDiceEvent, self.on_change_defender_dice)
        self.game.event_bus.subscribe(ChangeLossThresholdEvent, self.on_change_loss_threshold)
        self.game.event_bus.subscribe(FortifyPhaseStartedEvent, self.on_fortify_phase_started)
        self.game.event_bus.subscribe(NoFortifyLeftEvent, self.on_no_fortify_left)
        self.game.event_bus.subscribe(FortifyTerritoryEvent, self.on_fortify_territory)
        self.game.event_bus.subscribe(InvalidCommandEvent, self.on_invalid_command)
        self.updates_per_second = 8
        self.milliseconds_per_update = 1000 // self.updates_per_second 
        self.milliseconds_for_ai_thinking = 2000

    def start(self):
        self.after(1, self.game_auto_tick)
        self.mainloop()

    def game_auto_tick(self) -> None:
        if self.game.current_player in [controller.player for controller in self.ai_controllers]:
            self.after(self.milliseconds_for_ai_thinking, self.game_auto_tick)
        else:
            self.after(self.milliseconds_per_update, self.game_auto_tick)
        self.game.step()
        self.service.refresh()

    def transition_to_map_state(self) -> None:
        self.service.remove_all_widgets()
        self.service = MapStateService(self)

    def transition_to_battle_state(self, front: OffensiveFront) -> None:
        self.service.remove_all_widgets()
        self.service = BattleStateService(self, front)

    def transition_to_end_state(self, event: EndPhaseStartedEvent) -> None:
        self.service.remove_all_widgets()
        self.service = EndStateService(self)
    
    def on_territory_view_toggled(self, event: ViewTerritoriesEvent) -> None:
        if isinstance(self.service, MapStateService):
            self.service.territory_view_enabled = True

    def on_continent_view_toggled(self, event: ViewContinentsEvent) -> None:
        if isinstance(self.service, MapStateService):
            self.service.territory_view_enabled = False
    
    def on_card_view_toggled(self, event: ViewCardsEvent) -> None:
        if isinstance(self.service, MapStateService):
            if self.service.card_highlight_enabled:
                self.service.card_highlight_enabled = False
            elif not self.service.card_highlight_enabled:
                self.service.card_highlight_enabled = True
    
    def on_placement_phase_started(self, event: PlacementPhaseStartedEvent) -> None:
        self.transition_to_map_state()
        if self.game.rules.PLACEMENT == PlacementRules.MANUAL_PLACEMENT:
            GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name}, your placement phase has started!")

    def on_placement_phase_fortifying(self, event: PlacementPhaseFortifyingEvent) -> None:
        GenericTextOnlyPopUpWindow(self, description_text="All territories have now been claimed!")

    def on_unit_placed(self, event: PlaceUnitEvent) -> None:
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)

    def on_recruitment_phase_started(self, event: RecruitmentPhaseStartedEvent) -> None:
        if isinstance(self.service, MapStateService):
            self.service.first_territory_clicked = None
        GenericTextOnlyPopUpWindow(self, description_text="The recruitment phase has started!")

    def on_forced_card_trade(self, event: RequiredTradeEvent) -> None:
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name}, you must trade in a set!")
    
    def on_expecting_transfer(self, event: ExpectingTransferEvent) -> None:
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name}, you must transfer at least {event.front.attacker_dice} units to {event.front.territory_to}")

    def on_recruited_units(self, event: UnitsRecruitedEvent) -> None:
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name}, you recruited {event.units_recruited} units from bonuses!")

    def on_trade_set(self, event: TradeSetEvent) -> None:
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name} traded cards for {event.units_received} units!" if not event.error else event.error)

    def on_attack_phase_started(self, event: AttackPhaseStartedEvent) -> None:
        GenericTextOnlyPopUpWindow(self, description_text="The attack phase has started!")

    def on_focus_offensive(self, event: FocusOffensiveEvent) -> None:
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)
        elif event.front.status == BattleStatus.EXPECTING_TRANSFER:
            self.transition_to_map_state()
        else:
            self.transition_to_battle_state(event.front)

    def on_cancel_offensive(self, event: CancelFocusOffensiveEvent) -> None:
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)
        else:
            self.transition_to_map_state()
    
    def on_manual_attack(self, event: AttackManualEvent) -> None:
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)
        elif isinstance(self.service, BattleStateService):
            self.service.update_dice_rolls(event.attacker_rolls, event.defender_rolls)
        if self.game.state.front and self.game.state.front.status == BattleStatus.JUST_CAPTURED: 
            text = ""
            smallest_dice_set = min(event.attacker_rolls, event.defender_rolls, key=lambda rolls: len(rolls))
            largest_dice_set = min(event.attacker_rolls, event.defender_rolls, key=lambda rolls: len(rolls))
            for _ in range(len(largest_dice_set) - len(smallest_dice_set)):
                smallest_dice_set.append(0)
            for attacker_roll, defender_roll in zip(event.attacker_rolls, event.defender_rolls):
                text += f"{attacker_roll} - {defender_roll}\n"
            if event.territory_from.units == 1:     
                text += f"{event.territory_from.owner.name}, your attack has been repelled!"
            elif event.territory_to.units == 0:
                text += f"{event.territory_from.owner.name}, your attack was successful!"
            GenericTextOnlyPopUpWindow(self, description_text=text)

    def on_simulate_attack(self, event: AttackSimulateEvent) -> None:
        if not event.error:
            text = f"{event.territory_from.name} has lost {event.total_attacker_units_lost} and now has {event.territory_from.units} units left! \n"
            text += f"{event.territory_to.name} has lost {event.total_defender_units_lost} and now has {event.territory_to.units} units left!"
            GenericTextOnlyPopUpWindow(self, description_text=text)
        else:
            print(event.error)

    def on_change_attacker_dice(self, event: ChangeAttackerDiceEvent):
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)
    
    def on_change_defender_dice(self, event: ChangeDefenderDiceEvent):
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)
    
    def on_change_loss_threshold(self, event: ChangeLossThresholdEvent):
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)

    def on_fortify_territory(self, event: FortifyTerritoryEvent):
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)

    def on_attack_successful(self, event: AttackSuccessfulEvent):
        self.transition_to_map_state()

    def on_attack_repelled(self, event: AttackRepelledEvent):
        self.transition_to_map_state()

    def on_no_attacks_left(self, event: NoAttacksLeftEvent):
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name}, you have no attacks remaining!")

    def on_continent_captured(self, event: ContinentCapturedEvent):
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name} captured continent {event.continent.name}!")

    def on_card_received(self, event: CardReceivedEvent):
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name}, you have received a card showing a {event.card.unit} unit and the territory {event.card.territory}!")

    def on_invalid_command(self, event: InvalidCommandEvent):
        GenericTextOnlyPopUpWindow(self, description_text=event.error)

    #Fortify phase
    def on_fortify_phase_started(self, event: FortifyPhaseStartedEvent):
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name}'s fortify phase has started!")

    def on_no_fortify_left(self, event: NoFortifyLeftEvent):
        GenericTextOnlyPopUpWindow(self, description_text="There are no valid fortification moves!")

    #End phase
    def on_end_phase_started(self, event: EndPhaseStartedEvent):
        self.transition_to_end_state(event)

    def on_player_eliminated(self, event: PlayerEliminatedEvent):
        GenericTextOnlyPopUpWindow(self, description_text=f"{event.player.name} has been eliminated from the game!")

    def on_cards_transferred(self, event: CardsTransferredEvent):
        text = "Cards Transferred:\n"
        for card in event.cards:
            text += f"Territory: {card.territory}, Unit Shown: {card.unit}\n"
        GenericTextOnlyPopUpWindow(self, description_text=text)

    def on_next_turn(self, event: NextTurnEvent):
        if event.error:
            GenericTextOnlyPopUpWindow(self, description_text=event.error)

    def on_load(self, event: LoadGameEvent):
        if isinstance(self.game.state, AttackState) and self.game.front and self.game.front.status != BattleStatus.EXPECTING_TRANSFER:
            self.transition_to_battle_state(self.game.front)
        else:
            self.transition_to_map_state()

    def on_save(self, event: SaveGameEvent):
        GenericTextOnlyPopUpWindow(self, description_text="File successfully saved!")

class StateService(ABC):
    @abstractmethod
    def __init__(self, root: LocalPlayGUI):
        self.root: LocalPlayGUI = root
        self.active_widgets: list[tkinter.Widget] = []

    @abstractmethod
    def initialise_widgets(self) -> None:
        pass

    def remove_all_widgets(self) -> None:
        for widget in self.active_widgets:
            widget.destroy()
        self.active_widgets = []

    @abstractmethod
    def refresh(self) -> None:
        for widget in self.active_widgets:
            if hasattr(widget, "refresh") and callable(widget.refresh):
                widget.refresh()

class MapStateService(StateService):
    def __init__(self, root: LocalPlayGUI):
        super().__init__(root)
        self.first_territory_clicked = None
        self.territory_view_enabled = True
        self.card_highlight_enabled = False
        self.initialise_widgets()
    
    def initialise_widgets(self) -> None:
        self.remove_all_widgets()
        leaderboard = PlayerLeaderboard(self.root)
        leaderboard.place(x=820, y=0, width=300, height=720)
        self.active_widgets.append(leaderboard)
        number_of_units_button = NumberOfUnitsLeftButton(self.root)
        number_of_units_button.place(x=100, y= 600)
        self.active_widgets.append(number_of_units_button)
        self.__create_map_window_side_widgets()        
        if self.root.game.rules.MAP == MapRules.TRADITIONAL:
            conversion_table = TerritoryBonusTable(self.root)
            conversion_table.pack(side="bottom")
            self.active_widgets.append(conversion_table)
            self.__create_traditional_map_only_widgets()
        elif self.root.game.rules.MAP == MapRules.ANTIQUITY:
            self.__create_antiquity_map_only_widgets()

    def refresh(self) -> None:
        for widget in self.active_widgets:
            if isinstance(widget, (TerritoryButton, PlayerLeaderboard)):
                widget.refresh()
            elif isinstance(widget, NumberOfUnitsLeftButton):
                widget.refresh()
                if widget.units_left.get() == "0":
                    widget.place_forget()
                else:
                    widget.place(x=100, y= 600)

    def on_territory_button_clicked(self, territory_button: TerritoryButton) -> None:
        territory = territory_button.territory
        
        if isinstance(self.root.game.state, (PlacementState, RecruitmentState)):
            if isinstance(self.root.game.state, PlacementState):
                self.root.game.execute(PlaceUnitCommand(territory, 1))
            elif isinstance(self.root.game.state, RecruitmentState):
                EntryCommandWindow(self.root,
                                   PlaceUnitCommand,
                                   int,
                                   territory,
                                   description_text="Input number of units to place",
                                   submit_button_text="Place"
                                   )

        elif isinstance(self.root.game.state, (AttackState, FortificationState)):
            if isinstance(self.root.game.state, AttackState) and self.root.game.current_player.units_to_place > 0:
                EntryCommandWindow(self.root,
                                   PlaceUnitCommand,
                                   int,
                                   territory,
                                   description_text="Input number of units to place",
                                   submit_button_text="Place"
                                   )    
                
            if not self.first_territory_clicked: 
                self.first_territory_clicked = territory

            elif self.first_territory_clicked:
                if self.first_territory_clicked == territory:
                    self.first_territory_clicked = None #Clicking the same territory twice in a row should disregard it
                elif isinstance(self.root.game.state, AttackState) and not self.root.game.state.front:
                    self.root.game.execute(FocusOffensiveCommand(self.first_territory_clicked, territory))
                elif isinstance(self.root.game.state, FortificationState) or self.root.game.state.front.status == BattleStatus.EXPECTING_TRANSFER:
                    EntryCommandWindow(self.root, 
                                        FortifyTerritoryCommand,
                                        int,
                                        self.first_territory_clicked,
                                        territory,
                                        description_text="Input how many units you are transferring",
                                        submit_button_text="Transfer"
                                        )
                self.first_territory_clicked = None


    def __create_map_window_side_widgets(self) -> None:
        button_frame = tkinter.Frame(self.root, width=120, height=720)
        button_frame.pack(side="left", fill="y")
        self.active_widgets.append(button_frame)
        save_command_window = lambda: EntryCommandWindow(self.root,
                                                         SaveCommand,
                                                         str,
                                                         description_text="Input the name of the save file to write to(overwrites old files)",
                                                         submit_button_text="Save"
                                                         )

        load_command_window = lambda: EntryCommandWindow(self.root,
                                                LoadCommand,
                                                str,
                                                description_text="Input the save file to load from",
                                                submit_button_text="Load"
                                                )
        
        trade_set_window = lambda: TradeSetWindow(self.root,
                                                  self.root.game.current_player
                                                 )

        save_button = tkinter.Button(button_frame, text="Sa", command= save_command_window, width=4, height=4)
        load_button = tkinter.Button(button_frame, text="Lo", command= load_command_window, width=4, height=4)
        view_territories = tkinter.Button(button_frame, text="Te", command=lambda: self.root.game.execute(ViewTerritoriesCommand()), width=4, height=4)
        view_continents = tkinter.Button(button_frame, text="Co", command=lambda: self.root.game.execute(ViewContinentsCommand()), width=4, height=4)
        view_cards = tkinter.Button(button_frame, text="Ca", command=lambda: self.root.game.execute(ViewCardsCommand()), width=4, height=4)
        trade_set = tkinter.Button(button_frame, text="Tr", command= trade_set_window, width=4, height=4)
        next_turn = tkinter.Button(button_frame, text="Ne", command=lambda: self.root.game.execute(NextTurnCommand()), width=4, height=4)

        for i, button in enumerate([save_button, load_button, view_territories, view_continents, view_cards, trade_set, next_turn]):
            self.active_widgets.append(button)
            button.grid(row=i, column = 0)
        
    def __create_traditional_map_only_widgets(self) -> None:
        TERRITORY_POSITIONS = {
            "alaska": (80, 40),
            "northwest_territory": (180, 40),
            "greenland": (290, 40),
            "alberta": (80, 120),
            "ontario": (180, 120),
            "quebec": (280, 120),
            "western_united_states": (80, 200),
            "eastern_united_states": (180, 200),
            "central_america": (120, 280),

            "venezuela": (180, 360),
            "peru": (120, 440),
            "brazil": (220, 440),
            "argentina": (180, 520),

            "ukraine": (580, 120),
            "iceland": (380, 40),
            "scandinavia": (480, 40),
            "ural": (580, 40),
            "great_britain": (380, 120),
            "northern_europe": (480, 120),
            "western_europe": (380, 200),
            "southern_europe": (480, 200),

            "north_africa": (360, 360),
            "egypt": (460, 360),
            "congo": (380, 440),
            "east_africa": (460, 440),
            "south_africa": (460, 520),
            "madagascar": (560, 520),

            "ural": (580, 40),
            "siberia": (680, 40),
            "yakutsk": (780, 40),
            "irkutsk": (680, 120),
            "kamchatka": (780, 120),
            "mongolia": (680, 200), 
            "japan": (780, 200),
            "afghanistan": (580, 200),
            "china": (780, 280),
            "middle_east": (560, 280),
            "india": (680, 280),
            "siam": (660, 360),

            "indonesia": (680, 440),
            "new_guinea": (780, 440),
            "western_australia": (680, 520),
            "eastern_australia": (760, 520),
        }

        for territory_id, (x, y) in TERRITORY_POSITIONS.items():
            territory = self.root.game.board.get_territory_from_id(territory_id)
            territory_button = TerritoryButton(self.root, territory)
            territory_button.place(x=x, y=y, height=60, width=80)
            self.active_widgets.append(territory_button)


    def __create_antiquity_map_only_widgets(self) -> None:
        TERRITORY_POSITIONS = {
            "great_britain": (300, 200),
            "scandinavia": (400, 200),
            "western_europe": (260, 300),
            "northern_europe": (360, 300),
            "southern_europe": (460, 300),
            "ukraine": (560, 300),

            "north_africa": (275, 420),
            "egypt": (370, 420),
            "east_africa": (460, 450),

            "middle_east": (560, 400),
            "afghanistan": (670, 375),
            "ural": (670, 275),
}

        for territory_id, (x, y) in TERRITORY_POSITIONS.items():
            territory = self.root.game.board.get_territory_from_id(territory_id)
            territory_button = TerritoryButton(self.root, territory)
            territory_button.place(x=x, y=y, height=60, width=80)
            self.active_widgets.append(territory_button)

class BattleStateService(StateService):
    def __init__(self, root: LocalPlayGUI, offensive_front: OffensiveFront):    
        super().__init__(root)
        self.offensive_front = offensive_front
        self.initialise_widgets()

    def initialise_widgets(self) -> None:        
        self.attacking_territory_button = TerritoryButton(self.root, self.offensive_front.territory_from)
        self.active_widgets.append(self.attacking_territory_button)
        self.attacking_territory_button.place(x=200, y=200, width=200, height=200)
        self.attacking_territory_button.configure(font=("arial", 40 if len(self.offensive_front.territory_from.name) < 14 else 30))
        self.attacking_territory_button.territory_name.configure(font=("arial", 20))

        self.attacking_dice_used = tkinter.StringVar(value=f"Attacking dice: {self.offensive_front.attacker_dice}")
        self.attacking_dice_used_label = tkinter.Label(self.root, textvariable=self.attacking_dice_used, font=("arial", 14))
        self.active_widgets.append(self.attacking_dice_used_label)
        self.attacking_dice_used_label.place(x=200, y=420, width=200)
        
        self.attacker_dice_rolls_frame = tkinter.Frame(self.root, relief="solid", borderwidth=1)
        self.attacker_dice_rolls_frame.place(x=200, y=460, width=200, height=200)
        self.active_widgets.append(self.attacker_dice_rolls_frame)

        self.attacker_name_label = tkinter.Label(self.root, text=f"Attacker \n{self.offensive_front.territory_from.owner.name}", font=("arial", 15))
        self.attacker_name_label.place(x=300, y=40, anchor="center")
        self.active_widgets.append(self.attacker_name_label)

        attacker_dice_title = tkinter.Label(self.attacker_dice_rolls_frame, text="Attacker Rolls", font=("arial", 12))
        attacker_dice_title.pack(pady=5)

        self.defending_territory_button = TerritoryButton(self.root, self.offensive_front.territory_to)
        self.active_widgets.append(self.defending_territory_button)
        self.defending_territory_button.place(x=680, y=200, width=200, height=200)
        self.defending_territory_button.configure(font=("arial", 40 if len(self.offensive_front.territory_to.name) < 14 else 30))
        self.defending_territory_button.territory_name.configure(font=("arial", 20))

        self.defending_dice_used = tkinter.StringVar(value=f"Defending dice: {self.offensive_front.defender_dice}")
        self.defending_dice_used_label = tkinter.Label(self.root, textvariable=self.defending_dice_used, font=("arial", 14))
        self.active_widgets.append(self.defending_dice_used_label)
        self.defending_dice_used_label.place(x=680, y=420, width=200)
        
        self.defender_dice_rolls_frame = tkinter.Frame(self.root, relief="solid", borderwidth=1)
        self.defender_dice_rolls_frame.place(x=680, y=460, width=200, height=200)
        self.active_widgets.append(self.defender_dice_rolls_frame)
        
        self.defender_name_label = tkinter.Label(self.root, text=f"Defender \n{self.offensive_front.territory_to.owner.name}", font=("arial", 15))
        self.defender_name_label.place(x=780, y=40, anchor="center")
        self.active_widgets.append(self.defender_name_label)

        defender_dice_title = tkinter.Label(self.defender_dice_rolls_frame, text="Defender Rolls", font=("arial", 15))
        defender_dice_title.pack(pady=5)

        self.loss_threshold = tkinter.StringVar(value=f"Loss threshold: {self.offensive_front.loss_threshold}")
        self.loss_threshold_label = tkinter.Label(self.root, textvariable=self.loss_threshold, font=("arial", 16))
        self.active_widgets.append(self.loss_threshold_label)
        self.loss_threshold_label.place(x=440, y=100, width=200)

        self.__create_map_window_side_widgets()

    def __create_map_window_side_widgets(self) -> None:
        button_frame = tkinter.Frame(self.root, width=120, height=720)
        button_frame.pack(side="left", fill="y")
        self.active_widgets.append(button_frame)

        change_attacker_dice_window = lambda: EntryCommandWindow(self.root,
                                                                 ChangeAttackerDiceCommand,
                                                                 int,
                                                                 description_text="How many dice will the attacker be using?",
                                                                 submit_button_text="Submit")
        
        change_defender_dice_window = lambda: EntryCommandWindow(self.root,
                                                                 ChangeDefenderDiceCommand,
                                                                 int,
                                                                 description_text="How many dice will the defender be using?",
                                                                 submit_button_text="Submit")
        
        change_loss_threshold_window = lambda: EntryCommandWindow(self.root,
                                                                 ChangeLossThresholdCommand,
                                                                 int,
                                                                 description_text="How many units until the attacker should automatically stop?",
                                                                 submit_button_text="Submit")
        
        manual_attack = tkinter.Button(button_frame, text="Ma", command=lambda: self.root.game.execute(AttackManualCommand()), width=4, height=4)
        simulate_attack = tkinter.Button(button_frame, text="Si", command=lambda: self.root.game.execute(AttackSimulateCommand()), width=4, height=4)
        change_attacker_dice = tkinter.Button(button_frame, text="At", command=change_attacker_dice_window, width=4, height=4)
        change_defender_dice = tkinter.Button(button_frame, text="De", command=change_defender_dice_window, width=4, height=4)
        change_loss_threshold = tkinter.Button(button_frame, text="Lt", command=change_loss_threshold_window, width=4, height=4)
        cancel_front = tkinter.Button(button_frame, text="Ca", command=lambda: self.root.game.execute(CancelFocusOffensiveCommand()), width=4, height=4)

        for i, button in enumerate([manual_attack, simulate_attack, change_attacker_dice, change_defender_dice, change_loss_threshold, cancel_front]):
            self.active_widgets.append(button)
            button.grid(row=i, column=0)
    
    def refresh(self) -> None:
        for widget in self.active_widgets:
            if hasattr(widget, "refresh") and callable(widget.refresh):
                widget.refresh()
        
        self.defending_dice_used.set(f"Defending dice used: {self.offensive_front.defender_dice}")
        self.attacking_dice_used.set(f"Attacking dice used: {self.offensive_front.attacker_dice}")
        self.loss_threshold.set(f"Loss threshold: {self.offensive_front.loss_threshold}")
        self.attacking_territory_button.units_store.set(self.offensive_front.territory_from.units)
        self.defending_territory_button.units_store.set(self.offensive_front.territory_to.units)

    def on_territory_button_clicked(self, territory: Territory) -> None:
        pass

    def update_dice_rolls(self, attacker_rolls: list[int], defender_rolls: list[int]) -> None:
        for widget in self.attacker_dice_rolls_frame.winfo_children():
            widget.destroy()
        
        for widget in self.defender_dice_rolls_frame.winfo_children():
            widget.destroy()

        for roll in attacker_rolls:
            dice_rolled = tkinter.Label(self.attacker_dice_rolls_frame, text=roll, font=("arial", 30))
            dice_rolled.pack(fill="y")

        for roll in defender_rolls:
            dice_rolled = tkinter.Label(self.defender_dice_rolls_frame, text=roll, font=("arial", 30))
            dice_rolled.pack(fill="y")
        
class EndStateService(StateService):
    def __init__(self, root: LocalPlayGUI):
        super().__init__(root)
        self.current_player_focused_index = 0
        self.total_game_players = self.root.game.players + self.root.game.eliminated_players
        self.total_game_stats = self.root.game.stats
        self.initialise_widgets()
        self.root.game.event_bus.subscribe(NextTurnEvent, self.show_next_player_stats)
    
    def initialise_widgets(self) -> None:
        game_over_text = tkinter.Label(self.root, text="The game has finished!", font=("arial", "15"))
        self.active_widgets.append(game_over_text)
        game_over_text.pack(anchor="center", side="top")

        next_player_button = tkinter.Button(self.root, command=lambda: self.root.game.execute(NextTurnCommand()), text="Next")
        self.active_widgets.append(next_player_button)
        next_player_button.place(x=100, y=600, width=100, height=100)

        quit_button = tkinter.Button(self.root, command=sys.exit, text="Quit")
        self.active_widgets.append(quit_button)
        quit_button.place(x=820, y=600, width=100, height=100)

        load_command_window = lambda: EntryCommandWindow(self.root,
                                                LoadCommand,
                                                str,
                                                description_text="Input the save file to load from",
                                                submit_button_text="Load"
                                                )
        load_button = tkinter.Button(self.root, command=load_command_window, text="Load")
        self.active_widgets.append(load_button)
        load_button.place(x=490, y=600, width=100, height=100)

        total_game_stats = GameStatsFrame(self.root, self.total_game_stats)
        self.active_widgets.append(total_game_stats)
        total_game_stats.pack(anchor="nw", side="left")
        
        self.player_stats_frame = PlayerStatsFrame(self.root, self.total_game_players[self.current_player_focused_index])
        self.active_widgets.append(self.player_stats_frame)
        self.player_stats_frame.pack(anchor="ne", side="right")

        player_podium = PodiumFrame(self.root)
        self.active_widgets.append(player_podium)
        player_podium.pack(side="top", pady=10)

    def show_next_player_stats(self, event: NextTurnEvent) -> None:
        self.current_player_focused_index += 1
        self.current_player_focused_index %= len(self.total_game_players)
        self.player_stats_frame.show_new_player_stats(self.total_game_players[self.current_player_focused_index])

    def refresh(self) -> None:
        pass

class GameStatsFrame(tkinter.Frame):
    def __init__(self, root: LocalPlayGUI, stats: GameStats):
        super().__init__(root)
        self.root = root
        self.stats = stats
        self.active_widgets = []
        self.initialise_widgets()
    
    def initialise_widgets(self) -> None:
        self.stats: GameStats
        for stat in self.stats.__dict__:
            stat_display_text = " ".join(word.capitalize() for word in stat.split("_"))
            label = tkinter.Label(self, text=f"{stat_display_text}: {getattr(self.stats, stat)}", font=("arial", 20), padx=10, pady=10)
            self.active_widgets.append(label)
            label.pack(anchor="nw")

class PodiumFrame(tkinter.Frame):
    def __init__(self, root: LocalPlayGUI) -> None:
        super().__init__(root)
        self.root = root
        self.widgets = []
        self.positions = self.get_player_positions()
        self.initialise_widgets()

    #Players are sorted in their position in the game rankings, i=0 is 1st, i=1, is 2nd etc. 
    def get_player_positions(self) -> list[Player]:
        if self.root.game.rules.WIN_CONDITION == WinConditionRules.HUNDRED_PERCENT:
            return [self.root.game.players[0]] + self.root.game.eliminated_players[::-1]

        elif self.root.game.rules.WIN_CONDITION == WinConditionRules.SEVENTY_PERCENT:
            return sorted(self.root.game.players, key=lambda player: len(self.root.game.board.get_friendly_territories(player)), reverse=True) + self.root.game.eliminated_players[::-1]
    
    def initialise_widgets(self) -> None:
        base_ordinals = {1: "st", 2: "nd",3: "rd"}
        for i, player in enumerate(self.positions, start=1):
            if i <= len(base_ordinals):
                player_text = f"{i}{base_ordinals[i]}: {player.name}"
            else:
                player_text = f"{i}th: {player.name}"
            label = tkinter.Label(self, text=player_text, font=("arial", 15))
            label.pack(anchor="center") 
            
class PlayerStatsFrame(tkinter.Frame):
    def __init__(self, root: LocalPlayGUI, player: Player):
        super().__init__(root)
        self.root = root
        self.player = player
        self.active_widgets = []
        self.initialise_widgets()
    
    def show_new_player_stats(self, player: Player):
        self.player = player
        for widget in self.active_widgets:
            widget.destroy()
        self.initialise_widgets()

    def initialise_widgets(self) -> None:
        label=tkinter.Label(self, text=f"Player: {self.player.name}", font=("arial", 12))
        self.active_widgets.append(label)
        label.pack(anchor="ne")
        for stat in self.player.stats.__dict__:
            if stat == "total_dice_value":
                label=tkinter.Label(self, text=f"Average Dice roll: {str(self.player.stats.avg_dice_value)[:4]}", font=("arial", 12), padx=10, pady=10)#round to 2dp
            else:
                stat_display_text = " ".join(word.capitalize() for word in stat.split("_"))
                label = tkinter.Label(self, text=f"{stat_display_text}: {getattr(self.player.stats, stat)}", font=("arial", 12), padx=10, pady=10)
            label.pack(anchor="ne")
            self.active_widgets.append(label)

class NumberOfUnitsLeftButton(tkinter.Button):
    def __init__(self, root: LocalPlayGUI):
        super().__init__(root, width=5, height=3, bg="cyan", activebackground="cyan", relief="flat")
        self.root = root
        self.units_left = tkinter.StringVar(value=root.game.current_player.units_to_place)
        self.configure(textvariable=self.units_left)
    
    def refresh(self):
        self.units_left.set(self.root.game.current_player.units_to_place)

class TerritoryButton(tkinter.Button):
    def __init__(self, root: LocalPlayGUI, territory: Territory):
        self.territory = territory
        self.continent = root.game.board.get_continent_of_territory(territory)
        self.root = root
        self.units_store = tkinter.IntVar(value=self.territory.units)

        super().__init__(root,
                         width = 80,
                         height = 60,
                         bg=territory.owner.colour if territory.owner else "gray",
                         activebackground=territory.owner.colour if territory.owner else "gray",
                         textvariable=self.units_store,
                         command=lambda: root.service.on_territory_button_clicked(self)
                         )
        
        self.territory_name = tkinter.Label(self, 
                                            text=territory.name, 
                                            bg=territory.owner.colour if territory.owner else "gray",
                                            font=("Arial", 10 if len(territory.name) < 14 else 6)
                                           )
        self.territory_name.bind("<Button-1>", lambda event: root.service.on_territory_button_clicked(self))
        self.territory_name.pack()

    def refresh(self) -> None: 
        if isinstance(self.root.service, MapStateService):
            if self.root.service.territory_view_enabled:
                self.units_store.set(self.territory.units)
                colour = self.territory.owner.colour if self.territory.owner else "gray"
                self.configure(bg=colour, activebackground=colour)
                self.territory_name.configure(bg=colour)

            elif not self.root.service.territory_view_enabled:
                self.units_store.set(self.continent.bonus)
                colour = self.continent.colour
                self.configure(bg=colour, activebackground=colour)
                self.territory_name.configure(bg=colour)

            if self.root.service.card_highlight_enabled and self.territory.owner:
                colour = None
                for player in self.root.game.players:
                    if self.territory.id in [card.territory for card in player.cards]:
                        colour = player.colour
                        break
                if colour:
                    self.configure(highlightbackground=colour, highlightthickness=3)
                else:
                    self.configure(highlightthickness=0)
            else:         
                self.configure(highlightthickness=0)


class GenericTextOnlyPopUpWindow(tkinter.Toplevel):
    def __init__(self, root: LocalPlayGUI, description_text: str = "", submit_button_text = "Ok"):
        super().__init__(root)
        self.geometry("600x150")
        self.root = root

        description = tkinter.Label(self, text=description_text)
        button = tkinter.Button(self, text=submit_button_text, command=self._submit)

        description.place(anchor="center", relx=0.5, rely = 0.2)
        button.place(anchor="center", relx=0.5, rely=0.8)

    def _submit(self):
        self.destroy()
        #Should be polymorphed for subclass instances.

class PlayerLeaderboard(tkinter.Frame):
    def __init__(self, root: LocalPlayGUI): 
        super().__init__(root, width=300, height=720)
        self.pack_propagate(False)
        self.root = root

        self.player_labels = []
        self.__create_widgets()

    def __create_widgets(self) -> None:
        self.current_player_flag = tkinter.Label(self, text="NO", bg="gold")
        self.next_player_flag = tkinter.Label(self, text="NE", bg="purple")

        for i, player in enumerate(self.root.game.players):
            label = PlayerLeaderboardIndividual(self, player)
            label.place(x=90, y=25+100*i)
            self.player_labels.append(label)
        self.current_player = None

    def refresh(self) -> None:
        #We want to repack the GUI as sparingly as possible to avoid having the leaderboard flicker. 
        #This code makes it so that the GUI only updates the order visually only when an order change 
        #Has actually occured.
        player_deleted = False
        for label in self.player_labels:
            if label.player in self.root.game.eliminated_players:
                player_deleted = True
                label.destroy()
                self.player_labels.remove(label)

        sorted_labels = sorted(self.player_labels,
                            key=lambda label: len(self.root.game.board.get_friendly_territories(label.player)),
                            reverse=True
                            )

        if sorted_labels != self.player_labels or player_deleted:
            self.player_labels = sorted_labels
            for i, label in enumerate(self.player_labels):
                label.place_forget()
                label.place(x=90, y=25+100*i)

                self.current_player_flag.place_forget()
                self.next_player_flag.place_forget()
        
        for i, player in enumerate([label.player for label in self.player_labels]):
            if self.root.game.player_queue.head == player:
                if self.current_player_flag.winfo_y() != 25+100*i:
                    self.current_player_flag.place_forget()
                    self.current_player_flag.place(x=64, y=25+100*i, height=80, width=26)
                
            elif len(self.root.game.player_queue.body) > 1 and self.root.game.player_queue.body[1] == player:
                if self.next_player_flag.winfo_y() != 25+100*i:
                    self.next_player_flag.place_forget()
                    self.next_player_flag.place(x=64, y=25+100*i, height=80, width=26)

        for label in self.player_labels:
            label.refresh()

class PlayerLeaderboardIndividual(tkinter.Frame):
    def __init__(self, root: PlayerLeaderboard, player: Player):
        super().__init__(root,
                         width=175,
                         height=80,
                         bg="black"
                        )
        self.root = root
        self.game = root.root.game
        self.player = player
        self.pack_propagate(False)

        self.territories_text = tkinter.StringVar()
        self.units_text = tkinter.StringVar()
        self.cards_text = tkinter.StringVar()
        self.queue_text = tkinter.StringVar()

        if self.player in self.game.eliminated_players:
            return
        
        self.configure(bg=player.colour, padx=5, pady=5)

        player_name_label = tkinter.Label(self, text=player.name, bg=player.colour)
        player_name_label.pack(side="top", anchor="w")

        self.update_territory_text()
        territories_label = tkinter.Label(self, textvariable=self.territories_text, bg=player.colour)
        territories_label.pack(side="left", anchor="w")

        self.update_units_text()
        units_label = tkinter.Label(self, textvariable=self.units_text, bg=player.colour)
        units_label.pack(side="left", anchor="w")

        self.update_cards_text()
        cards_label = tkinter.Label(self, textvariable=self.cards_text, bg=player.colour)
        cards_label.pack(side="left", anchor="w")

        self.update_queue_text()
        queue_label = tkinter.Label(self, textvariable=self.queue_text, bg=player.colour)
        queue_label.pack(side="left", anchor="w")

    def refresh(self) -> None:
        self.update_territory_text()
        self.update_units_text()
        self.update_cards_text()
        self.update_queue_text()

    def update_territory_text(self) -> None:
        number_of_territories = len(self.game.board.get_friendly_territories(self.player))
        self.territories_text.set(f"T: {number_of_territories}")

    def update_units_text(self) -> None:
        self.number_of_units = sum(territory.units for territory in self.game.board.get_friendly_territories(self.player))
        self.units_text.set(f"U: {self.number_of_units}")

    def update_cards_text(self) -> None:
        number_of_cards = len(self.player.cards)
        self.cards_text.set(f"C: {number_of_cards}")

    def update_queue_text(self) -> None:
        position_in_queue = self.game.player_queue.body.index(self.player)
        self.queue_text.set(f"Q: {position_in_queue}")


class TerritoryBonusTable(tkinter.Frame):
    def __init__(self, parent: tkinter.Toplevel):
        super().__init__(parent)
        self.configure(relief="solid", borderwidth=1)
        self.__create_widgets()
    
    def __create_widgets(self):
        title = tkinter.Label(
                            self,
                            text="TERRITORY BONUS",
                            pady=5
                            )
        title.pack()
        
        territory_row = tkinter.Frame(self, relief="solid", borderwidth=1)
        territory_row.pack()
        
        units_row = tkinter.Frame(self, relief="solid", borderwidth=1)
        units_row.pack()
        
        for territories in range(0, 41, 3):
            units = max(3, territories//3)
            
            territory_label = tkinter.Label(
                                            territory_row,
                                            text=f"{territories}-{territories + 2}",
                                            width=6
                                            )
            territory_label.pack(side="left", padx=2)
            
            units_label = tkinter.Label(
                                        units_row,
                                        text=units,
                                        width=6
                                       )
            units_label.pack(side="left", padx=2)


class EntryCommandWindow(GenericTextOnlyPopUpWindow):
    def __init__(self, root: LocalPlayGUI,
                command_to_execute: Command,
                input_datatype: type, #All entry inputs are strings, but some commands expect integers for example.
                *command_parameters,
                description_text: str="",
                submit_button_text: str="Ok",
                ):
        super().__init__(root, description_text, submit_button_text)
        self.input_datatype = input_datatype
        self.command_to_execute = command_to_execute
        self.command_parameters = command_parameters

        self.user_input = tkinter.StringVar()
        input_box = tkinter.Entry(self, textvariable=self.user_input)
        input_box.place(anchor="center", relx=0.5, rely=0.5)

    def _submit(self) -> None:
        user_input = self.user_input.get().strip()

        try: 
            self.root.game.execute(self.command_to_execute(*self.command_parameters, self.input_datatype(user_input)))
        except:
            GenericTextOnlyPopUpWindow(self.root, "Invalid input!")
        finally:
            self.destroy()

class TradeSetWindow(tkinter.Toplevel):
    def __init__(self, root: LocalPlayGUI, player: Player):
        super().__init__(root)
        self.root = root
        self.player = player
        self.selected_cards = []
        self.__create_widgets()

    def __create_widgets(self) -> None:
        if not self.player.cards:
            label = tkinter.Label(self, text="This player has no cards to trade in!", fg="red")
            button = tkinter.Button(self, text="Cancel", command=self.destroy)
            label.grid(row=0, column=0) 
            button.grid(row=1, column=0)

        else:
            for i, card in enumerate(self.player.cards):
                is_checked = tkinter.BooleanVar(value=False)
                checkbox = tkinter.Checkbutton(self, 
                                               text=f"{i}: Territory shown: {card.territory}, Unit shown: {card.unit}", 
                                               variable=is_checked,
                                               command=lambda card=card, i_c=is_checked: self.__update_selected_cards(card, i_c)
                                               )
                #Must use lambda variables for card and is_checked because otherwise it evaluates ALL checkboxes
                #To use the data of the last item in the for loop.
                checkbox.grid(row=i, column=0)

            button = tkinter.Button(self, text="Submit", command=self._submit)
            button.grid(row=len(self.player.cards) + 1, column=0)
    
    def __update_selected_cards(self, card: Card, is_checked: tkinter.BooleanVar):
        if is_checked.get():
            if card not in self.selected_cards:
                self.selected_cards.append(card)
        
        elif not is_checked.get():
            if card in self.selected_cards:
                self.selected_cards.remove(card)

    def _submit(self) -> None:
        self.root.game.execute(TradeSetCommand(self.selected_cards))
        self.destroy()




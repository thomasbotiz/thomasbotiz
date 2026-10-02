from model import *

class ConsoleController:
    def __init__(self, game: Optional[Game] = None):
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
            if request[0] == "trade":
                cards = []
                for i in range(len(request[1:])):
                    cards.append(self.game.current_player.cards[i-1])
                parameters.append(cards)
            
            else:
                for parameter in request[1:]:
                    if parameter.strip("-").isdigit():
                        parameters.append(int(parameter))
                    else:
                        if request[0] in ["transfer", "place", "transfer", "focus"]:
                            territory = self.game.get_territory_from_id(parameter)
                            if not territory:
                                parameters.append(parameter)
                            else:
                                parameters.append(territory)
                        else:
                            parameters.append(parameter)
            command = command_type(*parameters)
            self.game.execute(command)

        except Exception as e:
            print("Could not interpret your command!")
            print(e)

class ConsoleView:
    def __init__(self, game: Game):
        self.game = game
        
        self.game.event_bus.subscribe(ViewContinentsEvent, self._on_view_continents)
        self.game.event_bus.subscribe(ViewTerritoriesEvent, self._on_view_territories)
        self.game.event_bus.subscribe(ViewCardsEvent, self._on_view_cards)
        self.game.event_bus.subscribe(InvalidCommandEvent, self._on_invalid_command)
        self.game.event_bus.subscribe(LoadGameEvent, self._on_load)
        self.game.event_bus.subscribe(SaveGameEvent, self._on_save)
        self.game.event_bus.subscribe(NextTurnEvent, self._on_next_turn)
        self.game.event_bus.subscribe(CloseGameEvent, self._on_close_game)
        self.game.event_bus.subscribe(PlacementPhaseStartedEvent, self._on_placement_phase_started)
        self.game.event_bus.subscribe(PlacementPhaseAutoSetupEvent, self._on_placement_phase_auto_setup)
        self.game.event_bus.subscribe(PlacementPhaseNextPlayer, self._on_placement_phase_next_player)
        self.game.event_bus.subscribe(PlacementPhaseFortifyingEvent, self._on_placement_phase_fortifying)
        self.game.event_bus.subscribe(PlacementPhaseEndedEvent, self._on_placement_phase_ended)
        self.game.event_bus.subscribe(UnplacedUnitsEvent, self._on_unplaced_units)
        self.game.event_bus.subscribe(PlaceUnitEvent, self._on_unit_placed)
        self.game.event_bus.subscribe(RecruitmentPhaseStartedEvent, self._on_recruitment_phase_started)
        self.game.event_bus.subscribe(RecruitmentPhaseEndedEvent, self._on_recruitment_phase_ended)
        self.game.event_bus.subscribe(NoRecruitmentLeftEvent, self._on_no_recruitment_left)
        self.game.event_bus.subscribe(ForcedCardTradeEvent, self._on_forced_card_trade)
        self.game.event_bus.subscribe(UnrecruitedUnitsEvent, self._on_unrecruited_units)
        self.game.event_bus.subscribe(UnitsRecruitedEvent, self._on_recruited_units)
        self.game.event_bus.subscribe(TradeSetEvent, self._on_trade_set)
        self.game.event_bus.subscribe(AttackPhaseStartedEvent, self._on_attack_phase_started)
        self.game.event_bus.subscribe(AttackPhaseEndedEvent, self._on_attack_phase_ended)
        self.game.event_bus.subscribe(NoAttacksLeftEvent, self._on_no_attacks_left)
        self.game.event_bus.subscribe(ActiveFrontEvent, self._on_active_front)
        self.game.event_bus.subscribe(CardReceivedEvent, self._on_card_received)
        self.game.event_bus.subscribe(AttackSuccessfulEvent, self._on_attack_successful)
        self.game.event_bus.subscribe(ExpectingTransferEvent, self._on_expecting_transfer)
        self.game.event_bus.subscribe(AttackAutoChangeDiceEvent, self._on_attack_auto_change_dice)
        self.game.event_bus.subscribe(AttackRepelledEvent, self._on_attack_repelled)
        self.game.event_bus.subscribe(ContinentCapturedEvent, self._on_continent_captured)
        self.game.event_bus.subscribe(PlayerEliminatedEvent, self._on_player_eliminated)
        self.game.event_bus.subscribe(CardsTransferredEvent, self._on_cards_transferred)
        self.game.event_bus.subscribe(RequiredTradeEvent, self._on_required_trade)
        self.game.event_bus.subscribe(LastPlayerLeftEvent, self._on_last_player_left)
        self.game.event_bus.subscribe(FocusOffensiveEvent, self._on_focus_offensive)
        self.game.event_bus.subscribe(CancelFocusOffensiveEvent, self._on_cancel_focus_offensive)
        self.game.event_bus.subscribe(AttackManualEvent, self._on_attack_manual)
        self.game.event_bus.subscribe(AttackSimulateEvent, self._on_attack_simulate)
        self.game.event_bus.subscribe(ChangeAttackerDiceEvent, self._on_change_attacker_dice)
        self.game.event_bus.subscribe(ChangeDefenderDiceEvent, self._on_change_defender_dice)
        self.game.event_bus.subscribe(ChangeLossThresholdEvent, self._on_change_loss_threshold)
        self.game.event_bus.subscribe(FortifyPhaseStartedEvent, self._on_fortify_phase_started)
        self.game.event_bus.subscribe(NoFortifyLeftEvent, self._on_no_fortify_left)
        self.game.event_bus.subscribe(FortifyPhaseEndedEvent, self._on_fortify_phase_ended)
        self.game.event_bus.subscribe(FortifyTerritoryEvent, self._on_fortify_territory)
        self.game.event_bus.subscribe(PlayerCycledEvent, self._on_player_cycled)
        self.game.event_bus.subscribe(EndPhaseStartedEvent, self._on_end_phase_started)

    def _on_view_continents(self, event: ViewContinentsEvent):
        for continent in event.continents:
            print(f"Continent ID: {continent.id}, Owner: {continent.owner.name if continent.owner else "No owner"}, Bonus Units: {continent.bonus}")
            territories = [territory.name for territory in continent.territories]
            print(f"This continent is comprised of: {" ".join(territories)}")
    
    def _on_view_territories(self, event: ViewTerritoriesEvent):
        for territory in event.territories:
            territories = [connected_territory.id for connected_territory in territory.connected_territories]
            print(f"Territory ID: {territory.id}, Owner: {territory.owner.name if territory.owner else "No owner"}, Units: {territory.units}, Connected Territories: {" ".join(territories)}")
        
    def _on_view_cards(self, event: ViewCardsEvent):
        if event.cards:
            print(f"{event.player.name}, you have cards with properties:")
            for i in range(len(event.cards)):
                print(f"{i+1}: Unit shown: {event.cards[i].unit}, Territory shown: {event.cards[i].territory}")
        else:
            print(f"{event.player.name}, you have no cards to show!")

    def _on_invalid_command(self, event: InvalidCommandEvent):
        print("Error! Your command failed to execute!\n" + event.error)

    def _on_load(self, event: LoadGameEvent):
        if not event.error:
            print("File loaded successfully!")
        else:
            print(event.error)

    def _on_save(self, event: SaveGameEvent):
        if not event.error:
            print(f"File {event.file_name} saved successfully!")
        else:
            print(event.error)

    def _on_next_turn(self, event: NextTurnEvent):
        if not event.error:
            print("Phase has ended!")
        else:
            print(event.error)

    def _on_close_game(self, event: CloseGameEvent):
        print("Application failed to close!")
 
    def _on_placement_phase_next_player(self, event: PlacementPhaseNextPlayer):
        print(f"Player {event.player.name}'s turn - You have {event.units_to_place} total unit(s)!")

    def _on_placement_phase_fortifying(self, event: PlacementPhaseFortifyingEvent):
        print(f"All territories have now been claimed!")

    def _on_placement_phase_started(self, event: PlacementPhaseStartedEvent):
        print("The placement phase has started!")

    def _on_placement_phase_auto_setup(self, event: PlacementPhaseAutoSetupEvent):
        print("Automatically set up the placement phase!")

    def _on_placement_phase_ended(self, event: PlacementPhaseEndedEvent):
        print("The placement phase has ended!")

    def _on_unplaced_units(self, event: UnplacedUnitsEvent):
        print(f"{event.player.name}, you have {event.units_left} units left to place!")

    def _on_unit_placed(self, event: PlaceUnitEvent):
        if not event.error:
            print(f"{event.units_placed} units successfully placed on {event.territory.name} by {event.player.name}! There are now {event.territory.units} unit(s) on that territory!")
        else:
            print(event.error)

    def _on_recruitment_phase_started(self, event: RecruitmentPhaseStartedEvent):
        print("The recruitment phase has started!")

    def _on_recruitment_phase_ended(self, event: RecruitmentPhaseEndedEvent):
        print("The recruitment phase has now ended!")

    def _on_no_recruitment_left(self, event: NoRecruitmentLeftEvent):
        print(f"{event.player.name}, you have no more units to recruit!")

    def _on_forced_card_trade(self, event: ForcedCardTradeEvent):
        print(f"{event.player.name}, you have {event.number_of_cards} cards, which is over the limit of {event.card_limit}! Trade in at least one set!")

    def _on_unrecruited_units(self, event: UnrecruitedUnitsEvent):
        print(f"{event.player.name}, you have {event.units_to_recruit} units left to recruit!")

    def _on_recruited_units(self, event: UnitsRecruitedEvent):
        print(f"{event.player.name}, you have passively recruited {event.units_recruited} units from territories and continent bonuses!")

    def _on_trade_set(self, event: TradeSetEvent):
        if not event.error:
            print(f"{event.player.name}, you have successfully traded in three cards, granting {event.units_received} units!")
        else:
            print(event.error)

    def _on_attack_phase_started(self, event: AttackPhaseStartedEvent):
        print("The attack phase has started!")

    def _on_attack_phase_ended(self, event: AttackPhaseEndedEvent):
        print("The attack phase has ended!")

    def _on_no_attacks_left(self, event: NoAttacksLeftEvent):
        print(f"{event.player.name}, you have no more available attacks left!")

    def _on_active_front(self, event: ActiveFrontEvent):
        print(f"You are currently focusing on an offensive front!")
        print(f"{event.front.territory_from.owner.name} is attacking {event.front.territory_to.owner.name}'s territory: {event.front.territory_to.name} from territory: {event.front.territory_from.name}")
        print(f"{event.front.territory_from.name} has {event.front.territory_from.units} units and {event.front.territory_to.name} has {event.front.territory_to.units} units!") 
        print(f"Attacking dice: {event.front.attacker_dice}, Defending dice: {event.front.defender_dice}, Loss threshold: {event.front.loss_threshold}") 
        print("Attack, change dice/loss threshold, cancel or set a new front!")

    def _on_card_received(self, event: CardReceivedEvent):
        print(f"{event.player.name}, you have received a card showing a {event.card.unit} unit and the territory {event.card.territory}!")

    def _on_attack_successful(self, event: AttackSuccessfulEvent):
        print(f"{event.front.territory_from.owner.name} has successfully captured {event.front.territory_to.name} from {event.front.territory_to.owner.name} with {event.front.territory_from.units} units left on {event.front.territory_from.name}!")

    def _on_expecting_transfer(self, event: ExpectingTransferEvent):
        print(f"You must fortify {event.front.territory_to.name} from {event.front.territory_from.name} which has {event.front.territory_from.units} units! You must transfer at least {event.front.attacker_dice} units!")
    def _on_attack_auto_change_dice(self, event: AttackAutoChangeDiceEvent):
        print(f"There are now {event.attacker_dice} dice and {event.defender_dice} defender dice after concurring losses!")

    def _on_attack_repelled(self, event: AttackRepelledEvent):
        print(f"{event.territory_to.owner.name} has successfully repelled {event.territory_from.owner.name}'s attack on {event.territory_to.name} with {event.territory_to.units} units left!")

    def _on_continent_captured(self, event: ContinentCapturedEvent):
        print(f"{event.player.name}, you have successfully captured continent {event.continent.name}!")

    def _on_player_eliminated(self, event: PlayerEliminatedEvent):
        print(f"{event.player.name} has been eliminated from the game!")

    def _on_cards_transferred(self, event: CardsTransferredEvent):
        print(f"Transferring cards from eliminated player {event.player_from.name} to {event.player_to.name}!")
        for card in event.cards:
            print(f"Card Transferred: Unit shown - {card.unit}, Territory shown - {card.territory}")

    def _on_required_trade(self, event: RequiredTradeEvent):
        print(f"{event.player.name}, you must trade in a set!")

    def _on_last_player_left(self, event: LastPlayerLeftEvent):
        print(f"{event.player.name}, you are the last player remaining!")

    def _on_focus_offensive(self, event: FocusOffensiveEvent):
        if not event.error:
            print("Offensive successfully focused on!")
            print(f"{event.front.territory_from.owner.name} is attacking {event.front.territory_to.owner.name}'s territory: {event.front.territory_to.name} from territory: {event.front.territory_from.name}")
            print(f"{event.front.territory_from.name} has {event.front.territory_from.units} units and {event.front.territory_to.name} has {event.front.territory_to.units} units!") 
            print(f"Attacking dice: {event.front.attacker_dice}, Defending dice: {event.front.defender_dice}, Loss threshold: {event.front.loss_threshold}") 
            print("Attack, change dice/loss threshold, cancel or set a new front!")
        else:
            print(event.error)

    def _on_cancel_focus_offensive(self, event: CancelFocusOffensiveEvent):
        if not event.error:
            print("Offensive front successfully cancelled!")
        else:
            print(event.error)

    def _on_attack_manual(self, event: AttackManualEvent):
        if not event.error:
            print(f"Attacker vs Defender Rolls:")
            for i in range(max(len(event.attacker_rolls), len(event.defender_rolls))):
                print(f"{event.attacker_rolls[i] if i < len(event.attacker_rolls) else 0}  {event.defender_rolls[i] if i < len(event.defender_rolls) else 0}")
            print(f"{event.territory_from.name} has lost {event.attacker_units_lost} and now has {event.territory_from.units} units left!")
            print(f"{event.territory_to.name} has lost {event.defender_units_lost} and now has {event.territory_to.units} units left!")
        else:
            print(event.error)
            
    def _on_attack_simulate(self, event: AttackSimulateEvent):
        if not event.error:
            print(f"{event.territory_from.name} has lost {event.total_attacker_units_lost} and now has {event.territory_from.units} units left!")
            print(f"{event.territory_to.name} has lost {event.total_defender_units_lost} and now has {event.territory_to.units} units left!")
        else:
            print(event.error)
            
    def _on_change_attacker_dice(self, event: ChangeAttackerDiceEvent):
        if not event.error:
            print(f"Attacking player {event.player.name} is now using {event.count} dice!")
        else:
            print(event.error)

    def _on_change_defender_dice(self, event: ChangeDefenderDiceEvent):
        if not event.error:
            print(f"Defending player {event.player.name} is now using {event.count} dice!")
        else:
            print(event.error)

    def _on_change_loss_threshold(self, event: ChangeLossThresholdEvent):
        if not event.error:
            print(f"Attacking player's loss threshold is now {event.loss_threshold} units!")
        else:
            print(event.error)

    def _on_fortify_phase_started(self, event: FortifyPhaseStartedEvent):
        print(f"{event.player.name}'s turn, Fortify phase has started!")

    def _on_no_fortify_left(self, event: NoFortifyLeftEvent):
        print("There are no possible options to fortify!")

    def _on_fortify_phase_ended(self, event: FortifyPhaseEndedEvent):
        print("The fortify phase has ended!")

    def _on_fortify_territory(self, event: FortifyTerritoryEvent):
        if not event.error:
            print(f"{event.player.name} has successfully fortified {event.territory_to.name} with {event.units_transferred} units from {event.territory_from.name}!")
            print(f"{event.territory_from.name} now has {event.territory_from.units} units and {event.territory_to.name} now has {event.territory_to.units} units!")
        else:
            print(event.error)

    def _on_end_phase_started(self, event: EndPhaseStartedEvent):
        print("The end phase has started!")
        base_ordinals = {1: "st", 2: "nd",3: "rd"}
        for i, player in enumerate(event.players, start=1):
            print(f"{i}{base_ordinals[i] if i < 4 else "th"}: {player.name}")


        print(f"Total turns played: {event.stats.turns_played}")
        print(f"Total sets traded in: {event.stats.traded_in_sets}")
        print(f"Total unit eliminated: {event.stats.units_eliminated}")
        print(f"Total units recruited: {event.stats.units_recruited}")
        print(f"Total territories captured: {event.stats.territory_captures}")

    def _on_player_cycled(self, event: PlayerCycledEvent):
        print(f"Player {event.player.name} has been cycled to!")
        print(f"Total territories captured: {event.stats.total_territories_captured}")
        print(f"Total territories lost: {event.stats.total_territories_lost}")
        print(f"Total continents captured: {event.stats.total_continents_captured}")
        print(f"Total continents lost: {event.stats.total_continents_lost}")
        print(f"Total units recruited: {event.stats.total_units_recruited}")
        print(f"Total enemy units eliminated: {event.stats.total_enemy_units_eliminated}")
        print(f"Total friendly units eliminated: {event.stats.total_friendly_units_eliminated}")
        print(f"Offensive battles: {event.stats.offensive_battles}")
        print(f"Defensive battles: {event.stats.defensive_battles}")
        print(f"Offensive rolls: {event.stats.offensive_rolls}")
        print(f"Defensive rolls: {event.stats.defensive_rolls}")
        print(f"Total dice value: {event.stats.total_dice_value}")
        print(f"Average dice used while attacking: {event.stats.avg_attacking_dice_used}")
        print(f"Average dice used while defending: {event.stats.avg_defending_dice_used}")
        print(f"Average dice roll value: {event.stats.avg_dice_value}")


import discord
from discord import app_commands, Colour
from discord.ext import commands, tasks
from bs4 import BeautifulSoup, Comment
import requests
import datetime
import asyncio
from dataclasses import dataclass

class Team:
    def __init__(self, short_name = "NYY"):
        self.timestamp = datetime.datetime.min
        self.COOLDOWN = 900#900 Seconds(15 minutes) before refreshing the team statistics.
        self.short_name = short_name
        
        self.recent_game_raw_data = None
        self.recent_game_raw_data_pitching_scores = None
        self.recent_game_raw_data_batting_scores = None

        self.formatted_recent_game = ""
        self.formatted_pitching_scores = ""
        self.formatted_batting_scores = ""

        self.scraper = uniscraper

    def check_data_is_stale(self) -> bool:
        if (datetime.datetime.now() - self.timestamp).total_seconds() > self.COOLDOWN:#If past TTL
            return True
        else:
            return False

    async def fetch_latest_game(self):
        url = f"https://www.baseball-reference.com/teams/{self.short_name}/2025-schedule-scores.shtml"
        games = await self.scraper.fetch_records(url, "team_schedule")

        if not games:
            return 
        
        for game in games[::-1]:#iterate backwards until we find the first completed game
            if game["W/L"] in {"W", "L", "W-wo", "L-wo"}:
                self.recent_game_raw_data = game

    async def fetch_latest_box_scores(self):
        if not self.recent_game_raw_data:
            await self.fetch_latest_game()

        url = f"https://www.baseball-reference.com" + await self.fetch_most_recent_box_plot_url()
        ids = self.fetch_box_scores_tableid()

        self.recent_game_raw_data_batting_scores = await self.scraper.fetch_records(url, ids.batting_id)
        self.recent_game_raw_data_pitching_scores = await self.scraper.fetch_records(url, ids.pitching_id)

    async def fetch_most_recent_box_plot_url(self):
        if not self.recent_game_raw_data:
            await self.fetch_latest_game()
            
        return self.recent_game_raw_data["link"]
    
    @dataclass
    class BoxIDs:
        batting_id: str
        pitching_id: str

    def fetch_box_scores_tableid(self) -> BoxIDs:
        """
        Each team's box score has a unique id e.g. NYY = NewYorkYankeesbatting
        Translate abbreviation to full team name, remove spaces add batting/pitching 
        """
        team_id = TEAM_NAMES[self.short_name].replace(" ", "")
        batting_team_id = team_id + "batting"
        pitching_team_id = team_id + "pitching"
        ids = self.BoxIDs(batting_team_id, pitching_team_id)
        return ids

    async def create_results_embed(self):
        if not self.recent_game_raw_data:
            await self.fetch_latest_game()
        
        if self.check_data_is_stale():
            await self.fetch_latest_game()


        game_details = self.recent_game_raw_data
        relevant_stats = RESULT_STATS

        team = TEAM_NAMES[self.short_name]
        colour = discord.Colour.gold()

        opp = game_details["Opp"]
        opponent = TEAM_NAMES[opp]

        title = f"Last Game Results for {team} vs {opponent} "
        embed = discord.Embed(
        title=title,
        colour=colour)

        for requested_stat in relevant_stats:
            stat_display_name = relevant_stats[requested_stat]
            value = game_details[requested_stat]
            if requested_stat == "W/L":
                if value == "W": 
                    value = "✅"
                else:
                    value = "❌"
            if requested_stat == "Opp":
                continue    
            
            embed.add_field(name=stat_display_name, value=value, inline=True)


        self.formatted_recent_game = embed

    async def create_box_score_embed(self, box_score_type):
        """
        Manipulate the dictionary and create a string which 
        outputs cleanly on an embed
        box_score_type == "batting" or "pitching" 
        """
        if not self.recent_game_raw_data:
            await self.fetch_latest_game()
        
        if not self.recent_game_raw_data_batting_scores or not self.recent_game_raw_data_pitching_scores:
            await self.fetch_latest_box_scores()

        if box_score_type == "batting":
            box_scores = self.recent_game_raw_data_batting_scores
            relevant_stats = BATTING_STATS.keys()
            colour = discord.Colour.brand_red()
            key_for_name = "Batting"#player names are saved under "Batting"/"Pitching" respectively
            key_for_appearances = "AB"
        
        elif box_score_type == "pitching":
            box_scores = self.recent_game_raw_data_pitching_scores
            relevant_stats = PITCHING_STATS.keys()
            colour = discord.Colour.dark_blue()
            key_for_name = "Pitching"#player names are saved under "Batting"/"Pitching" respectively
            key_for_appearances = "IP"

        game_details = self.recent_game_raw_data
        game_date = game_details["Date"]

        opp = game_details["Opp"]
        opponent = TEAM_NAMES[opp]

        team = TEAM_NAMES[self.short_name]
        result = game_details["W/L"]

        attendance = game_details["Attendance"]
        
        if result == "W": 
            result = "✅"
        else:
            result = "❌"  

        title = f"{team} vs {opponent}\n"
        title += f"Winner: {result}, Date: {game_date}, Attendance: {attendance}\n"
        description = "```\n"
        description += "Batting Box Scores\n" if box_score_type == "batting" else "Fielding Box Scores\n"
        description += "Player".ljust(14)
        for stat in relevant_stats:
            description += stat.rjust(4)
        description += "\n"
        for player in box_scores:
            if not player[key_for_appearances]:
                continue
            if float(player[key_for_appearances]) == 0:#did not make an appearance
                continue

            player_name = player[key_for_name]
            player_name = self.format_name(player_name)

            description += player_name.ljust(14)#Names need more spacing 

            for stat in relevant_stats:
                if player[stat]:
                    description += player[stat].rjust(4)
                else:
                    description += "0"
            description += "\n"
        description += "```"  

        embed = discord.Embed(
            title = title,
            colour = colour,
            description = description
        )
        embed.set_footer(text="baseball-reference.com")

        if box_score_type == "batting":
            self.formatted_batting_scores = embed
        elif box_score_type == "pitching":
            self.formatted_pitching_scores = embed
                    
    def format_name(self, player_name: str):
        """
        Website uses a different unicode format, sometimes causes bizzare characters to show
        Fixes by first dropping accents then making the value ASCII """
        player_name = player_name.encode('ascii', 'ignore').decode('ascii')
        player_name = player_name.replace(",", "")
        if len(player_name) >= 2:
            parts = player_name.split()
            player_name = f"{parts[0][0]}. {parts[1]}"#only get the first initial and last name 
        return player_name
        

class Scraper:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.timestamp = datetime.datetime.min
        self.COOLDOWN = 3#min seconds between calls, to comply with robots.txt

    def check_cooldown_elapsed(self) -> bool:
        if (datetime.datetime.now() - self.timestamp).total_seconds() > self.COOLDOWN:
            return True
        else:
            return False

    async def fetch_records(self, url: str, table_id: str) -> list[dict]:
        """
        input: website url, table_id. table_id is obtained from scraping HTML
        returns a list of dictionaries, key = header description, value = record value
        also returns the hyperlink for boxscore as the last element
        """
        await self.lock.acquire()
        if not self.check_cooldown_elapsed():
            await asyncio.sleep(self.COOLDOWN)#To enable safe access concurrently
        try:        
            response = requests.get(url)
            response.raise_for_status()
            self.timestamp = datetime.datetime.now()
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", id = table_id)
            
            if not table:#In particular for box scores, which are commented out
                comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                for comment in comments:
                    comment_soup = BeautifulSoup(comment, "html.parser")
                    table = comment_soup.find("table", id=table_id)
                    if table:
                        break

            headers = table.find("thead").find_all("th")
            headers = [header.text for header in headers]

            body = table.find("tbody")
            records = body.find_all("tr")

            entries = []
            for record in records:
                link = ""
                record_data = record.find_all(["th", "td"])#Gm1 is stored as a header 
                values = [value.text for value in record_data]
                if table_id == "team_schedule":
                    boxscore = record.find("a", string = "boxscore")
                    if boxscore:
                        link = boxscore.get("href")

                entry = {header: value for header, value in zip(headers, values)}
                entry["link"] = link
                entries.append(entry)
            return entries
        
        except Exception as e:
            print(f"Error parsing '{url}', '{table_id}'! Perhaps table was changed? Error: {e}")
            return None

        finally:
            self.lock.release()

uniscraper = Scraper()
team_cache = {}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Successfully logged in!")
    auto_update.start()

@bot.tree.command(name="help", description="Get Team, Pitching, Batting, Results inputs.")
@app_commands.describe(
    requested = "Teams/Batting/Pitching/Results")
async def help(interaction, requested: str):
    await interaction.response.defer(ephemeral = True)

    requested = requested.capitalize().strip()
    response = ""
    if requested == "Teams":
        for abbreviation, team_name in TEAM_NAMES.items():
            response += f"**{abbreviation}**: {team_name} \n"
    elif requested == "Batting":
        for abbreviation, stat in BATTING_STATS.items():
            response += f"**{abbreviation}**: {stat} \n"
    elif requested == "Pitching":
        for abbreviation, stat in PITCHING_STATS.items():
            response += f"**{abbreviation}**: {stat} \n"
    elif requested == "Results":
        for abbreviation, stat in RESULT_STATS.items():
            response += f"**{abbreviation}**: {stat} \n"
    else:
        await interaction.followup.send("Invalid request! Options: Teams/Batting/Pitching/Results", ephemeral = True)
        return

    embed = discord.Embed(
        title= f"{requested}",
        description=response , 
        colour = Colour.teal()
    )

    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="batting_stats", description="Get Batting Box score from last game")
@app_commands.describe(
    team = "Team Abbreviation: (leave blank for NYY)")
async def batting(interaction, team: str = "NYY"):
    await interaction.response.defer(ephemeral = False)

    if team not in TEAM_NAMES:
        await interaction.followup.send("Invalid team abbreviation! Use /help Teams to see valid teams", ephemeral = True)
        return

    if team not in team_cache:
        team_cache[team] = Team(team)

    if not team_cache[team].formatted_batting_scores:
        await team_cache[team].create_box_score_embed("batting")

    embed = team_cache[team].formatted_batting_scores
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="pitching_stats", description="Get Pitching Box score from last game")
@app_commands.describe(
    team = "Team Abbreviation: (leave blank for NYY)")
async def pitching(interaction, team: str = "NYY"):
    await interaction.response.defer(ephemeral = False)

    if team not in TEAM_NAMES:
        await interaction.followup.send("Invalid team! Use /help Teams to see valid teams", ephemeral = True)
        return

    if team not in team_cache:
        team_cache[team] = Team(team)

    if not team_cache[team].formatted_pitching_scores:
        await team_cache[team].create_box_score_embed("pitching")

    embed = team_cache[team].formatted_pitching_scores
    await interaction.followup.send(embed=embed)

    
@bot.tree.command(name="results", description="Output the result of chosen team: (leave blank for NYY)")
@app_commands.describe(
    team = "Team Abbreviation: (leave blank for NYY)")
async def results(interaction, team: str = "NYY"):
    await interaction.response.defer(ephemeral = False)

    if team not in TEAM_NAMES:
        await interaction.followup.send("Invalid team! Use /help Teams to see valid teams.", ephemeral = True)
        return
    
    if team not in team_cache:
        team_cache[team] = Team(team)

    if not team_cache[team].formatted_recent_game:
        await team_cache[team].create_results_embed()

    embed = team_cache[team].formatted_recent_game
    await interaction.followup.send(embed=embed)

@tasks.loop(minutes = 7.5)
async def auto_update():
    """
    To reduce wait times, automatically cache the information about frequently accessed teams periodically:
    NYY, the team NYY most recently played, NYM, BRS
    """
    for team in ["NYY", "NYM", "BOS"]:
        if team not in team_cache:
            team_cache[team] = Team(team)
        
        if team_cache[team].check_data_is_stale():
            await team_cache[team].fetch_latest_box_scores()

    recent_opp = team_cache["NYY"].recent_game_raw_data["Opp"]
    
    if recent_opp not in team_cache:
        team_cache[recent_opp] = Team(recent_opp)
        
    if team_cache[recent_opp].check_data_is_stale():
        await team_cache[recent_opp].fetch_latest_box_scores()    

TEAM_NAMES = {
    "ARI": "Arizona Diamondbacks", 
    "ATL": "Atlanta Braves", 
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox", 
    "CHC": "Chicago Cubs", 
    "CHW": "Chicago White Sox",
    "CIN": "Cincinnati Reds", 
    "CLE": "Cleveland Guardians", 
    "COL": "Colorado Rockies",
    "DET": "Detroit Tigers", 
    "HOU": "Houston Astros", 
    "KCR": "Kansas City Royals",
    "LAA": "Los Angeles Angels", 
    "LAD": "Los Angeles Dodgers", 
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers", 
    "MIN": "Minnesota Twins", 
    "NYM": "New York Mets",
    "NYY": "New York Yankees", 
    "OAK": "Oakland Athletics", 
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates", 
    "SDP": "San Diego Padres", 
    "SEA": "Seattle Mariners",
    "SFG": "San Francisco Giants", 
    "STL": "St. Louis Cardinals", 
    "TBR": "Tampa Bay Rays",
    "TEX": "Texas Rangers", 
    "TOR": "Toronto Blue Jays", 
    "WSN": "Washington Nationals"
}

BATTING_STATS = {
    "AB": "At Bats",
    "R": "Runs Scored",
    "H": "Hits",
    "RBI": "Runs Batted In",
    "BB": "Bases on Balls",
    "SO": "Strikeouts",
    "PA": "Plate Appearances",
    "PO" : "Putouts",
    "A": "Assists"
}

PITCHING_STATS = {
    "IP": "Innings Pitched",
    "H": "Hits allowed",
    "R": "Runs allowed",
    "BB": "Bases on Balls",
    "SO": "Strikeouts",
    "HR": "Home Runs allowed",
    "BF": "Batters Faced",
    "Str": "Strikes",
    "Ctct": "Strikes by contact",
    "StS": "Strikes to swing and miss",
}

RESULT_STATS = {
    "W/L": "Win Loss Record",
    "Opp": "Opponent",
    "R": "Runs Scored",
    "RA": "Runs Allowed",
    "W-L": "Win Loss Record",
    "Date": "Date"
}


bot.run("")#Token required

import requests
import json

import time
from datetime import datetime

import logging
import math
import heapq

from dataclasses import dataclass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Market:
    """
        Wrapper for accessing the Hypixel API.

        This class encapsulates the market data and provides methods for accessing the market on a macro-scale

        Attributes:
            timestamp (datetime): The exact time the products were refreshed
            scraper (Scraper):  A custom scraper object(see Scraper)
            catalogue (Dict[List]): Holds bazaar product data, every key is a product_id, keys map to Item object (see Item)
            capital (float): Total number of coins to be invested
    """
    def __init__(self):

        self.timestamp = datetime.min
        self.scraper = Scraper()

        self.catalogue = {}
        self.capital = 0.0
        logger.info("Market Object successfully created!")


    def __update_catalogue(self) -> None:
        """
        Checks if the data needs to be refreshed, if so then fetch bazaar products from API and copy the new product data into the catalogue
        """
        if self.__check_if_data_stale():#prevent accidentally flooding the API 
            logger.info("Updating catalogue details!")
            self.timestamp = datetime.now()
            new_catalogue = self.scraper.fetch_catalogue()
            for product_id, product_data in new_catalogue.items():
                if product_id in self.catalogue:#Reduce overhead
                    self.catalogue[product_id].update_item(product_data)
                else:
                    self.catalogue[product_id] = Item(product_id, product_data)

    def __check_if_data_stale(self) -> bool: 
        """
        Private function to check if the data needs to be refreshed by comparing the time since the last update with the config TTL
        
        Returns:
            bool: True = Stale, False = Fresh
        """
        time_elapsed = (datetime.now() - self.timestamp).total_seconds()
        if time_elapsed > MarketConfig.DATA_TTL:
            return True
        else:
            return False
    
    def set_capital(self) -> float:
        try:
            self.capital = float(input("Input total capital at risk: (Leave blank for 1b)").strip())
        except: 
            if not self.capital:
                self.capital = 1000000000.0#1,000,000,000
                
    @dataclass
    class Flip:
        product_id: str
        profit_per_hour: float
        imbalance: str
        def __lt__(self, other):#Max heap instead of min heap
            return self.profit_per_hour < other.profit_per_hour

    def scan_for_flips(self) -> None:
        """
        Search all products for the best flips, prints a specific number of flips.

        The number of flips returned is dependant on MarketConfig.MAX_FLIPS_SHOWN   
        """
        if not self.capital:
            self.set_capital()
        if self.__check_if_data_stale():#No point recalculating if using the same data
            self.__update_catalogue()

            best_flips = []
            if self.catalogue:
                for product in self.catalogue.values():
                    if not product.is_tradeable():
                        continue

                    profit_per_hour = product.calculate_profit_per_hour(self.capital)
                    imbalance = product.calculate_book_imbalance()
                    flip = self.Flip(product.product_id, profit_per_hour, imbalance)
                    if len(best_flips) < MarketConfig.MAX_FLIPS_SHOWN:
                        heapq.heappush(best_flips, flip)
                    elif profit_per_hour > best_flips[0].profit_per_hour:
                        heapq.heapreplace(best_flips, flip)
        
            if best_flips:
                print(f"=== TOP {MarketConfig.MAX_FLIPS_SHOWN} BEST FLIPS ===")
                for flip in best_flips:
                    print(f"Potential flip: {flip.product_id}, Estimated revenue per hour: {flip.profit_per_hour}, imbalance: {flip.imbalance}")
            else:
                print("No flips could be found!")

class Item:
    """
    Encapsulates market data for a specific product.

    Holds financial methods

    Attributes:
        product_id (str): Product Name
        sell_summary (dict): Holds details about all active sell orders
        buy_summary (dict): Holds details about all active buy orders
        quick_status (dict): Holds basic market data about the object 
        """
    def __init__(self, product_id, product_data):
        self.product_id = product_id
        self.sell_summary = product_data["sell_summary"]
        self.buy_summary = product_data["buy_summary"]
        self.quick_status = product_data["quick_status"]

    #Object management methods
    def update_item(self, product_data: dict) -> None:
        """
        Copy the updated data into itself, then format the data to be more accurate
        
        Arguments:
            product_data (Dict): The new product data fetched from API"""
        

        self.sell_summary = product_data["sell_summary"]
        self.buy_summary = product_data["buy_summary"]
        self.quick_status = product_data["quick_status"]     
        self.refine_item()   

    def refine_item(self) -> None:
        """For every listing in an item's summary, remove all suspicious orders and group together similar orders"""
        self.sell_summary = self.remove_suspicious_orders(self.sell_summary)
        self.buy_summary = self.remove_suspicious_orders(self.buy_summary)
        self.sell_summary = self.group_similar_orders(self.sell_summary)
        self.buy_summary = self.group_similar_orders(self.buy_summary)

    @dataclass
    class Bundle:
        amount: int
        total_valuation: float
        orders: int 

    def group_similar_orders(self, summary: dict) -> list:
        """
        Players often bet +/- 0.1 coins on the orderbook to have their order fulfilled
        quicker, grouped data gives better information about the volume at a price   

        Arguments:
            summary (dict): Buy/Sell Summary 
        
        Returns:
            summary (dict): The same Buy/Sell Summary, grouped
        """https://discord.com/developers/docs/quick-start/getting-started
        if len(summary) <= 1:
            return summary
        
        final_summary = []
        new_bundle = self.Bundle(0, 0, 0)
        target_price = summary[0]["pricePerUnit"]
        for listing in summary:
            amount = listing["amount"]
            price = listing["pricePerUnit"]
            orders = listing["orders"]
            if self.check_similar_orders(target_price, price):
                new_bundle.amount += amount
                new_bundle.total_valuation += (price * amount)#So avg. is weighted by amount
                new_bundle.orders += orders
            else:
                grouped_orders = self.create_bundle(new_bundle)
                final_summary.append(grouped_orders)
                new_bundle = self.Bundle(amount, price*amount, orders)
        
        grouped_orders = self.create_bundle(new_bundle)
        final_summary.append(grouped_orders)
        return final_summary

    def check_similar_orders(self, price1: float, price2: float) -> bool:
        if self.calculate_percentage_difference(price1, price2) < MarketConfig.SAME_ORDER_THRESHOLD:
            return True
        else:
            return False

    def create_bundle(self, bundle: Bundle) -> dict:
        average_price = bundle.total_valuation / bundle.amount
        return {
            "amount": bundle.amount,
            "pricePerUnit" : average_price,
            "order": bundle.orders
            }

    def remove_suspicious_orders(self, summary: dict) -> dict:
        """
        Removes orders from the book by checking if the next item has a high difference in value AND much fewer people placing the order

        Strictness is dependant on MarketConfig.MANIPULATED_PRICE_THRESHOLD and MANIPULATED_ORDER_THRESHOLD

        Recursively checks elements if the top is manipulated to ensure that all manipulated listings have been removed.

        Arguments:
            summary (dict): The Buy/Sell Summary being checked for manipulation

        Returns:
            summary (dict): The same summary but with suspicious listings eliminated
        the bottom item is potentially manipulated so recurse until two consecutive listings are consistent."""
                
        if len(summary) <= 1:
            return summary
        
        order1 = summary[0]
        order2 = summary[1]

        if self.check_for_manipulation(order1, order2):
            return self.remove_suspicious_orders(summary[1:])#recurse until top value is consistent with second top
        else:
            return summary
    
    def check_for_manipulation(self, order1: dict, order2: dict) -> bool:
        """
        Note: heuristic approach. Success depends on how accurate the config values are,
        there will be false positives and false negatives.
        If one listing has much less orders(not to be confused with amount) and one listing is much cheaper/expensive,
        It is likely manipulated.
        """
        first_price = order1["pricePerUnit"]
        second_price = order2["pricePerUnit"]
        num_order1 = order1["amount"]
        num_order2 = order2["amount"]

        if self.calculate_percentage_difference(first_price, second_price) > MarketConfig.MANIPULATED_PRICE_THRESHOLD:
            if self.calculate_percentage_difference(num_order1, num_order2) > MarketConfig.MANIPULATED_ORDER_THRESHOLD:
                return True
        return False
    
    @staticmethod
    def calculate_percentage_difference(val1: float|int, val2: float|int) -> float:
        try:
            return abs((val1 - val2) / (val1 + val2) / 2) * 100
        except:
            if not isinstance(val1, (int, float)) or not isinstance(val2, (int, float)):
                logger.error(f"Calculation between {val1} and {val2} failed as invalid datatype!")
            if val2 == 0:
                logger.error(f"Calculation between {val1} and {val2} failed as val2 = 0!")
            return float("inf")
        
    #Financial Methods
    def is_tradeable(self) -> bool:
        """
        If no sell orders or no buy orders, then it is not liquid enough to trade
        """
        if len(self.buy_summary) > 0 and len(self.sell_summary) > 0:
            return True
        else:
            return False

    def fetch_cost(self) -> float:
        if self.buy_summary:
            top_listing = self.buy_summary[0]
            return top_listing["pricePerUnit"] 

    def fetch_price(self) -> float:
        if self.sell_summary:
            top_listing = self.sell_summary[0]
            return top_listing["pricePerUnit"]
        
    def fetch_quick_sell_cost(self) -> float:
        if self.quick_status:
            return self.quick_status["sellPrice"]
    
    def fetch_quick_buy_cost(self) -> float:
        if self.quick_status:
            return self.quick_status["buyPrice"]
        
    def fetch_buy_volume(self) -> float:
        if self.buy_summary:
            top_listing = self.buy_summary[0]
            return top_listing["amount"]  
            
    def fetch_sell_volume(self) -> float:
        if self.sell_summary:
            top_listing = self.sell_summary[0]
            return top_listing["amount"]  
    
    def calculate_max_buy_volume(self, capital: float) -> int:
        """
        Calculates how many items one can place a buy order for at the current market rate, accounting for price decreases

        Assumes price does not fluctuate and all buy orders will be fulfilled eventually

        Arguments:
            capital (float): Number of coins used to play buy orders
        
        Returns:
            total_quantity (int): The max number of items the player can buy
        """
        remaining_capital = capital
        total_quantity = 0
        
        for order in self.buy_summary:  
            price = order["pricePerUnit"]
            amount = order["amount"]
            
            affordable = math.floor(remaining_capital / price)
            take = min(affordable, amount)
            
            total_quantity += take
            remaining_capital -= take * price
            
            if remaining_capital <= 0:
                break
        
        return total_quantity

    def calculate_affordable_quantity(self, capital: float) -> int:#1,000,000
        quantity = math.floor(capital / self.fetch_cost())
        return quantity

    def calculate_sales_velocity(self) -> float:

        return (self.quick_status["buyMovingWeek"] / MarketConfig.HOURS_IN_WEEK)
    
    def calculate_purchase_velocity(self) -> float:
        """
        Calculates buy orders fulfilled per week
        """
        return (self.quick_status["sellMovingWeek"] / MarketConfig.HOURS_IN_WEEK)
    
    def calculate_velocity_cap(self) -> int:
        """
        Limit the number of a product that can be sold 
        """
        sales_per_hour = self.calculate_sales_velocity()
        purchases_per_hour = self.calculate_purchase_velocity()
        return int(min(sales_per_hour, purchases_per_hour))
    
    def calculate_velocity_limited_quantity(self, capital: float) -> int:
        """
        The velocity of the object is limited by how quickly one can flip 
        the product and how many total items the player can buy
        """
        affordable_quantity = self.calculate_affordable_quantity(capital)
        velocity_quantity = self.calculate_velocity_cap()
        return min(affordable_quantity, velocity_quantity)

    def calculate_absolute_profit(self, capital:float) -> float:
        quantity = self.calculate_affordable_quantity(capital)
        cost = self.fetch_cost()
        price = self.fetch_quick_buy_cost() * (1 - MarketConfig.BAZAAR_TAX/100)
        return (price - cost) * quantity
    
    def calculate_percentage_profit(self) -> float:
        cost = self.fetch_cost()
        price = self.fetch_quick_buy_cost() * (1 - MarketConfig.BAZAAR_TAX/100)
        return (price - cost) / cost * 100

    def calculate_profit_per_hour(self, capital: float) -> float:
        quantity = self.calculate_velocity_limited_quantity(capital)
        cost = self.fetch_cost()
        price = self.fetch_quick_buy_cost() * (1 - MarketConfig.BAZAAR_TAX / 100)
        profit_per_item = price - cost
        return profit_per_item * quantity
    
    def calculate_book_imbalance(self) -> str:
        """
        Uses book imbalance formula to predict if an item's value will rise or fall

        Items with more buy orders than sell orders are marked as Heavy sell, prices likely to rise

        Items with more sell orders than buy orders are marked as Heavy buy, prices likely to fall
        """
        sell_volume = self.fetch_sell_volume()
        buy_volume = self.fetch_buy_volume()
        if sell_volume + buy_volume > 0:
            imbalance = (sell_volume - buy_volume)/(sell_volume + buy_volume)
            if -1 <= imbalance < -0.33:
                return "Heavy sell"#Prices likely to rise
            elif -0.33 <= imbalance < -0.1:
                return "Light sell"
            elif -0.1 <= imbalance < 0.1:     
                return "Neutral"
            elif 0.1 <= imbalance < 0.33:
                return "Light buy"
            elif 0.33 <= imbalance <= 1.0:
                return "Heavy buy"#Prices likely to fall

@dataclass
class MarketConfig:
    """
    Attributes:
        DATA_TTL (int): product data is stale after X seconds
        BAZAAR_TAX (float): Percent Tax placed on only sell orders
        SAME_ORDER_THRESHOLD (float): Two products are treated the same if price is within X%
        MANIPULATED_PRICE_THRESHOLD (float): If percentage difference > X% flag as suspicious 
        MANIPULATED_ORDER_THRESHOLD (float): If percentage difference > X% disregard order
        HOURS_IN_WEEK (int): Number of hours in a week
        MAX_FLIPS_SHOWN (int): Max number of flips shown on a scan
    """

    DATA_TTL = 15 
    BAZAAR_TAX = 1.0
    SAME_ORDER_THRESHOLD = 1.0 
    MANIPULATED_PRICE_THRESHOLD = 50
    MANIPULATED_ORDER_THRESHOLD = 200
    HOURS_IN_WEEK = 168
    MAX_FLIPS_SHOWN = 10

class Scraper:
    """
    Wrapper which fetches the Hypixel Bazaar API

    Note that Bazaar API only suppports fetching of whole database

    Attributes:
        url (str): The URL being fetched from
        """
    def __init__(self):
        self.url = "https://api.hypixel.net/skyblock/bazaar"

    def fetch_catalogue(self) -> dict:
        """
        Scrape the API, returning only the products if successful.

        Returns:
            product_data(dict): All products if successful, otherwise empty
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()

            bazaar_products = response.json()
            if self.__validate_api_response(bazaar_products):
                logger.info("Catalogue successfully fetched from API!")
                return bazaar_products["products"]
            else:
                logger.error("Could not fetch catalogue from API!")
                return {}

        except Exception as e:
            logger.error(f"Unknown error {e} has occured while fetching from API!")
            return {}
     
    def __validate_api_response(self, bazaar_products: dict) -> bool:
        """
        Validates that the API response is structured correctly and  
        and check that API is functioning as expected.

        Returns:
            True if data validated successfully, False otherwise
        """
        if not bazaar_products:
            logger.error("No API response was given!")
            return False
        
        if not isinstance(bazaar_products, dict):
            logger.error("API response was not recognised!")
            return False
        
        required_keys = ["success", "lastUpdated", "products"]
        missing_keys = [key for key in required_keys if key not in bazaar_products]

        if missing_keys:
            logger.error(f"API response is missing required keys: {missing_keys}!")
            return False
        
        if bazaar_products["success"] != True:
            logger.error("API response was unsuccessful!")
            return False
        return True

market = Market()
while True:
    market.scan_for_flips()

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import sqlite3

def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

def get_items_by_name(name):
    item = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(f'''
            SELECT 
                I.is_recyclable, 
                I.name as item_name, 
                M.name as material_name 
            FROM item I
            INNER JOIN material M
                ON I.mid = M.id                
            WHERE I.name = '{name}' ''')
        item = cur.fetchall()        
        print("get item from sql:", item)
    except:
        print("get_items_by_name exception")
    return item

def get_locations_by_item_material(item_name='', material='', postcode=41200):
    locations = []    
    postcode = int(postcode)
    try:                
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()        
        
        range = 0
        while(range < 10000):                                 
            
            query = f'''
                SELECT DISTINCT L.*, RF.name, RF.url, ABS(L.postcode-{postcode}) AS distance
                    FROM item I
                    INNER JOIN material M
                        ON I.mid = M.id
                    INNER JOIN material_accept MA
                        ON M.id = MA.mid
                    INNER JOIN recycling_facility RF
                        ON MA.rfid = RF.id
                    INNER JOIN location L	
                        ON L.rfid = RF.id
                    WHERE I.name = '{item_name}'
            '''
            query += f" AND M.name = '{material}'" if material else ""
            query += f" AND L.postcode BETWEEN '{postcode-range}' AND '{postcode+range}'" if postcode else ""
            query += f" ORDER BY distance"
            print('-------------')
            print(query)
            print('-------------')
            cur.execute(query)
            locations = cur.fetchall()
            if len(locations):
                return locations
            range+=1000
    except:
        print("catch something wrong when executing sql statement")        

    return locations


class ActionAskIfSomethingRecyclable(Action):

    def name(self) -> Text:
        return "action_ask_if_something_recyclable"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        material = next(tracker.get_latest_entity_values("material"),None)
        item = next(tracker.get_latest_entity_values("item"),None)
        
        item_list = get_items_by_name(item)
        if not item_list or item in ["something","thing","object","article","item","product"]:
            dispatcher.utter_message(response=f"utter_repeat_slot_input")
            # dispatcher.utter_message(response=f"utter_prompt_suggest_item")
            return [SlotSet("item",None)]

        if len(item_list)>1:
            dispatcher.utter_message(text='There are few different material of this item')
            for i in item_list:
                message = f"{i['material_name']} {i['item_name']} is{'' if i['is_recyclable'] else 'not'} recyclable".capitalize()
                dispatcher.utter_message(text=message)            
        else:
            item_dict = item_list[0]            
            message = "Yes, it is recyclable" if item_dict["is_recyclable"] else "No, it is not recyclable"
            dispatcher.utter_message(text=message)        
        return True
        

class ActionAskSomethingRecyclableLocation(Action):

    def name(self) -> Text:
        return "action_ask_something_recyclable_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        item = tracker.get_slot('item')                
        
        item_list = get_items_by_name(item)
        print("(action_ask_something_recyclable_location) item list: ",len(item_list))
        if not item_list or item in ["something","thing","object","article","item","product"]:
            dispatcher.utter_message(response=f"utter_repeat_slot_input")
            # dispatcher.utter_message(response=f"utter_prompt_suggest_item")
            return [SlotSet("item",None)]
        
        material = tracker.get_slot('material') if tracker.get_slot('material') else None
        postcode = tracker.get_slot('postcode') if tracker.get_slot('postcode') else None

        location_list = get_locations_by_item_material(item,material,postcode)
        if len(location_list)>1:
            dispatcher.utter_message(text='Here are the few location: ')            
            for index, l in enumerate(location_list):
                message = f"{l['name'] if l['name'] else ''} {', '+l['title'] if l['title'] else ''} {', '+l['address'] if l['address'] else ''} {', '+l['details'] if l['details'] else ''}\n"
                # message = f"{l['name']}, {l['address']}\n"
                dispatcher.utter_message(text=message)
                if index%4==0:
                    break
                # return [SlotSet("item", None), SlotSet("postcode", None)]        
            return []
        elif len(location_list)==1:
            message = f"{l['name'][0] if l['name'][0] else ''} {', '+l['title'][0] if l['title'][0] else ''} {', '+l['address'][0] if l['address'][0] else ''} {', '+l['details'][0] if l['details'][0] else ''}\n"
            # message = f"{l['name']}, {l['address']}\n"
            dispatcher.utter_message(text=message)
        
        message = f"Dont have any nearby location for recycling {item}"
        dispatcher.utter_message(text=message)
        return True

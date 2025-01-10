import os
from supabase import create_client, Client
import logging

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def create_user(chat_id: int):
    """
    * creates a new user in the database
    """
    response = supabase.table("users").insert({"chat_id": chat_id}).execute()
    return response

def get_user_info(chat_id: str):
    """
    * checks if a user exists in the database
    """
    response = supabase.table("users").select().eq("chat_id", chat_id).execute()

    print(response)

    if response.data:
        return response.data[0]
    else:
        return None

def update_user_profile(chat_id, level: str, college: str):
    """
    * updates the user's level and college
    """
    response = supabase.table("users").update({"college": college, "level": level}).eq("chat_id", chat_id).execute()
    return response

def add_message(text: str, college: str, level: int):
    """
    * adds a message to the database
    """
    response = supabase.table("messages").insert({"message": text, "college": college, "level": level}).execute()
    return response

def filter_users(college: str, level: str):
    """
    * filters messages by college and level
    """
    query = supabase.table("users")
    if college == "All" and level == "All":
        response = query.select().execute()

    elif level == "All":
        response = query.select().eq("college", college).execute()
    
    elif college == "All":
        response = query.select().eq("level", level).execute()  
    
    else:
        response = query.select().eq("college", college).eq("level", level).execute()
    
    logging.info(response.data)
    return response 

def get_messages():
    """
    * gets all messages from the database
    """
    response = supabase.table("messages").select().execute()
    return response.data
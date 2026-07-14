from datetime import datetime,timedelta
from database import get_db_connection
from collections import defaultdict
import streamlit as st
def get_statistics(user_id):
    conn=get_db_connection()
    if not conn:
        return """
        "total_messages":0,
        "user_messages":0,
        "ai_messages":0,
        "total_words":0,
        "duration":00:00:00
    """
    total_messages=0
    user_mgs=0
    ai_msg=0
    total_words=0
    total_duration=timedelta()
    has_valid_duration=False
    query="""
        SELECT m.conversation_id,m.role,m.message,m.created_at FROM messages m JOIN conversations c ON m.conversation_id=c.id WHERE c.user_id=%s ORDER BY m.conversation_id,m.created_at ASC
    """
    try:
        cursor=conn.cursor(dictionary=True)
        cursor.execute(query,(user_id,))
        rows=cursor.fetchall()
        convo_messages=defaultdict(list)
        for row in rows:
            convo_messages[row['conversation_id']].append(row)
        for messages in convo_messages.values():
            total_messages+=len(messages)
            user_mgs+=sum(1 for msg in messages if msg["role"]=="user")        
            ai_msg+=sum(1 for msg in messages if msg["role"]=="assistant")
            total_words+=sum(len(msg["message"].split()) for msg in messages)
            if len(messages)>=2:
                try:
                    start=messages[0]["created_at"]
                    end=messages[-1]["created_at"]
                    if isinstance(start,str):
                        start=datetime.isoformat(start)
                    if isinstance(end,str):
                        end=datetime.isoformat(end)
                    total_duration+=(end-start)
                    has_valid_duration=True
                except Exception as err:
                    total_duration="Unavailable"
        return {
            "total_messages":total_messages,
            "user_messages":user_mgs,
            "ai_messages":ai_msg,
            "total_words":total_words,
            "duration":str(total_duration) if has_valid_duration else "0:00:00"
        }
    except Exception as e:
        st.error(f"Error calculating database analytics: {e}")
        return {
            "total_messages": 0,
            "user_messages": 0,
            "ai_messages": 0,
            "total_words": 0,
            "duration": "0:00:00"
        }
    finally:
        conn.close()

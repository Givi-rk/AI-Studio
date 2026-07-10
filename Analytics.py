from datetime import datetime,timedelta
import json
def get_statistics():
    with open("conversations.json","r") as f:
        data=json.load(f)
    total_messages=0
    user_mgs=0
    ai_msg=0
    total_words=0
    for convo in data.values():
       # print(convo)
        messages=convo["messages"]
        total_messages+=len(messages)
        user_mgs+=sum(1 for msg in messages if msg["role"]=="user")        
        ai_msg+=sum(1 for msg in messages if msg["role"]=="assistant")
        total_words+=sum(len(msg["message"].split()) for msg in messages)
        duration=timedelta()
        if len(messages)>=2:
            try:
                start=datetime.fromisoformat(messages[0]["timestamps"])
                end=datetime.fromisoformat(messages[-1]["timestamps"])
                duration+=(end-start)
            except Exception as err:
                print(err)
                duration="Unavailable"
        else:
            duration="0:00:00"
    return {
        "total_messages":total_messages,
        "user_messages":user_mgs,
        "ai_messages":ai_msg,
        "total_words":total_words,
        "duration":str(duration)
    }

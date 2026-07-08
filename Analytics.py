from datetime import datetime
def get_statistics(messages):
    total_messages=len(messages)
    user_mgs=sum(1 for msg in messages if ["role"]=="user")
    ai_msg=sum(1 for msg in messages if ["role"]=="assistant")
    total_words=sum(len(msg["message"].split()) for msg in messages)
    if len(messages)<=2:
        try:
            start=datetime.fromisoformat(messages[0])
            end=datetime.fromisoformat(messages[-1])
            duration=str(end-start)
        except Exception:
            duration="Unavailable"
    else:
        duration="0:00:00"
    return {
        "total_messages":total_messages,
        "user_messages":user_mgs,
        "ai_messages":ai_msg,
        "total_words":total_words,
        "duration":duration
    }

from datetime import datetime
def get_current_timestamp()-> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def compile_stats(history:list)->dict:
    total_messages=len(history)
    user_mgs=len([m for m in history if m["role"]=="user"])
    ai_mgs=len([m for m in history if m["role"]=="assistant"])
    total_words=sum(len(m["message"].split()) for m in history)
    return {
        "Total Messages":total_messages,
        "User Messages": user_mgs,
        "AI Messages": ai_mgs,
        "Total Words": total_words        
    }
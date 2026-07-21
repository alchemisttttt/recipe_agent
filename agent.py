import os
import json
from dotenv import load_dotenv
from groq import Groq
from pyexpat.errors import messages

from database import init_db, add_recipe, list_recipes, add_to_pantry, list_pantry, what_can_i_cook

load_dotenv()
client= Groq(api_key=os.getenv("GROQ_API_KEY"))
init_db()

tools=[
    {
        "type":"function",
        "function":{
            "name":"add_recipe",
            "description":"Save a specific recipe to the database. Only use this when the user explicitly provides a recipe's name and ingredients and asks to save/add it — never invent a recipe on your own.",
            "parameters":{
                "type":"object",
                "properties":{
                    "name":{"type":"string","description":"name of the recipe"},
                    "instructions":{"type":"string","description":"how to prepare the recipe"},
                    "ingredients":{"type":"array",
                        "items":{"type":"string"},
                        "description":"List of ingredient names needed, e.g. ['pasta', 'garlic']"},
                },
                "required":["name","instructions","ingredients"]
            }


        }
    },

    {
        "type":"function",
        "function":{
            "name":"list_recipes",
            "description":"List all saved recipes and their ingredients",
            "parameters":{
                "type":"object",
                "properties":{}
            }
        }
    },

    {
        "type":"function",
        "function":{
            "name":"add_to_pantry",
            "description":"Add one ingredient to the user's pantry",
            "parameters":{
                "type":"object",
                "properties":{
                    "ingredient_name":{"type":"string","description":"name of the ingredient to add"},
                },
                "required":["ingredient_name"]
            }
        }
    },

    {
        "type":"function",
        "function":{
            "name":"list_pantry",
            "description":"Show everything currently in the user's pantry",
            "parameters":{
                "type":"object",
                "properties":{}
            }
        }
    },

    {
        "type":"function",
        "function":{
            "name":"what_can_i_cook",
            "description":"Check which saved recipes the user has all the ingredients for, based on their pantry",
            "parameters":{
                "type":"object",
                "properties":{

                }
            }
        }

    }
]

av_functions={
    "add_recipe":add_recipe,
    "list_recipes":list_recipes,
    "add_to_pantry":add_to_pantry,
    "list_pantry":list_pantry,
    "what_can_i_cook":what_can_i_cook
}


SYSTEM_PROMPT = (
    "You are a helpful recipe and meal planning assistant. "
    "You have tools to add recipes, add pantry items, list recipes, list the pantry, "
    "and check what the user can cook.\n\n"
    "Use a tool ONLY when the user is clearly asking you to add, save, or check "
    "something specific in their data (e.g. 'add eggs to my pantry', 'save this recipe', "
    "'what's in my pantry', 'what can I cook').\n\n"
    "Do NOT use a tool when the user is asking a general question, asking for advice, "
    "asking how to cook something, or just chatting (e.g. 'what's healthy?', "
    "'how do I make pasta?', 'any tips?') — just answer normally in plain text using "
    "your own knowledge.\n\n"
    "Never invent or add a recipe unless the user explicitly gives you its name and "
    "ingredients and asks you to save/add it. "
    "After a tool runs, briefly confirm what happened in one short sentence. "
    "Never write out fake function calls or code-like syntax in your replies."
)

def run_agent(usr_msg:str,history:list):
 history.append({"role":"user","content":usr_msg})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=history,
            tools=tools,
        )
    except Exception as e:
        error_reply = "Sorry, I had trouble processing that — could you try rephrasing?"
        history.append({"role": "assistant", "content": error_reply})
        return error_reply

    msg= response.choices[0].message

    if msg.tool_calls:
        history.append(msg)
        func_name=None
        result=None

        for call in msg.tool_calls:
            func_name= call.function.name
            func_arg= json.loads(call.function.arguments) or {}

            print(f"[Agent is calling: {func_name}({func_arg})]")
            result = av_functions[func_name](**func_arg)

            history.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

        if func_name in ("list_recipes", "list_pantry", "what_can_i_cook"):
            history.append({"role": "assistant", "content": result})
            return result

        response_2 = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=history,
        )
        reply = response_2.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        return reply

    reply = msg.content
    history.append({"role": "assistant", "content": reply})
    return reply


if __name__ == "__main__":
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Recipe Agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        print("Agent:", run_agent(user_input, history))
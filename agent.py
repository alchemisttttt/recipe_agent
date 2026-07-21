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
            "description":"Add a new recipe with its name, instructions, and list of ingredients",
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
    "You are a helpful recipe and meal planning assistant. You manage the user's "
    "recipes and pantry using the tools available to you. Always use a tool when "
    "the user wants to add, view, or check something, rather than replying in text. "
    "After a tool runs, briefly confirm what happened in one short sentence. "
    "Never write out fake function calls or code-like syntax in your replies."
)

def run_agent(usr_msg:str,history:list):
    history.append({"role":"user","content":usr_msg})
    response= client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history,
        tools=tools,
    )

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
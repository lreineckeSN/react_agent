import asyncio
from dotenv import load_dotenv
from openai.lib.azure import AsyncAzureOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
import re
import json

load_dotenv()

client = AsyncAzureOpenAI()


async def fetch_completion(user_prompt: str, system_prompt: str, history):
    response = await client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[ChatCompletionUserMessageParam(content=user_prompt, role="user"),
                  ChatCompletionSystemMessageParam(content=system_prompt, role="system"),
                  ChatCompletionSystemMessageParam(content=str(history), role="system")],
    )
    return response.choices[0].message.content


def add(a, b) -> int:
    return a + b


def multiply(a, b) -> int:
    return a * b


tools_map = {'Add': add, 'Multiply': multiply}


async def mathematical_ai(prompt: str):
    system_prompt = """You are a mathematical AI. You receive mathematical questions. You can call tools. You havbe 
    the following tools: {name: Multiply, description: This tool multiplies two integer numbers. inputs: {a: {type: 
    int, description: factor}, b: {type: int, description: factor} {name: Add, description: This tool adds two 
    integer numbers. inputs: {a: {type: int, description: summand}, b: {type: int, description: summand} {name: 
    Finish, description: Gives the answer to the user, inputs: {a: {type: string, description: The answer you want to 
    give the user. This answer must strive for excellence. Only in full sentences}} You can call tools in the 
    following way: Action\\s*\\d*\\s*: Name of the tool[\\s]* Action\\s*\\d*\\s*Input\\s*\\d*\\s*:[dictionary of 
    parameter in this way "parameter_name": parameter_value] When generating an answer always follow this format: 
    Think: <think> Act: <call a Tool> If you get the output of a tool add Observe: <observe the latest tool output"""
    history = ""
    while True:
        response = await fetch_completion(prompt, system_prompt, history)
        print(response)
        tool_name, params = re.search(r"Action\s*\d*\s*:\s*(.*?)\s*Action\s*\d*\s*Input\s*\d*\s*:\s*(.*)",
                                      response).groups()
        params_dict = json.loads(params)
        if tool_name == "Finish":
            break
        tool = tools_map.get(tool_name.capitalize())
        history += response
        history += "tool_output: " + str(tool(**params_dict))
    return params_dict.get('a')


prompt_text = "Multiply 3 times 4 and add 5"
final = asyncio.run(mathematical_ai(prompt_text))
print(final)

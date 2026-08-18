from openai import OpenAI
import json

def get_openai_client(openai_api_key):
    # timeout/max_retries bound how long a single call can stall the caller.
    client = OpenAI(
        api_key=openai_api_key,
        base_url="https://api.deepseek.com",
        timeout=20.0,
        max_retries=1,
    )
    return client

def check_message_relevancy_with_llm(client, msg, llm_prompt):

    response = client.chat.completions.create(
        model="deepseek-chat",
        response_format={
            'type': 'json_object'
        },
        messages =[
            {
                "role": "system",
                "content": llm_prompt
            },
            {
                "role": "user",
                "content": msg
            }
        ],
    )

    return response.choices[0].message.content

def parse_json(text):
    parsed_json = None
    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
    return parsed_json

def parse_bool(text):
    if type(text) == bool:
        return text
    return text.lower() == 'true'


if __name__ == "__main__":
    from config import openai_api_key
    from test_cases.llm_tests import test_msgs
    from tqdm import tqdm

    client = get_openai_client(openai_api_key)

    num_tests = len(test_msgs)
    correct_tests = 0

    for msg in tqdm(test_msgs):
        
        response = check_message_relevancy_with_llm(client, msg.get('msg'))
        response = parse_json(response)
        if parse_bool(response.get("is_relevant")) == msg.get("is_relevant"):
            correct_tests += 1
        print(msg.get("msg"))
        print(response)
        print(parse_bool(response.get('is_relevant')))
            
    
    print(f"Correct tests: {correct_tests}/{num_tests}")
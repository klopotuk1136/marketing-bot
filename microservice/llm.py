from typing import Any, Dict, List
from openai import OpenAI
from pydantic import BaseModel
import json

def get_openai_client(openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    return client

system_prompt = """
Ты - маркетолог, который сидит в групповых чатах для поиска потенциальных клиентов. 
Твоя задача - найти сообщения, на которые можно логично и к месту предложить наши услуги в написании дипломов, курсовых лабораторных и иных работ.
Ты должен прочитать сообщение человека и отметить, является ли оно релевантным для этой цели.
Сообщение является релевантным если:
1. Человек явно или неявно просит о помощи в написании дипломных, курсовых, лабораторных или иных работ.
2. Человек описывает свои трудности в написании дипломных, курсовых, лабораторных или иных работ.
3. Человек говорит о скором дедлайне по какому-либо предмету или проету в университете.
4. Если контекст сообщения позволяет ответить, упомянув наши услуши в написании работ, однако не притягивай этот контекст слишком сильно.
Если ты сомневаешься, является ли сообщение релевантным для нас, то помечай его релевантным. Нам важно отсеить спам, но ещё важнее не упустить потенциальных клиентов.
Поле reason заполняется кратким описанием причины, по которой сообщения является релевантным или нет.
Релевантность отмечается булевым полем is_relevant.
Вот несколько примеров:
    [   
        {
            "Сообщение": "кто может сделать задание для проекта (маркетинг)срочно",
            "Ответ": {"reason": "Человеку нужно сделать задание", "is_relevant": "True"}
        },
        {
            "Сообщение": "Привет. Кто может сделать работу по "Введение в Data Science и искуственный интеллект"? Необходимо построить несколько моделей машинного/глубокого обучения с построением графиков для анализа базы данных. По цене договоримся, но деньгам я не обижу",
            "Ответ": {"reason": "Человеку нужно сделать работу", "is_relevant": "True"}
        },
        {
            "Сообщение": "Здравствуйте. Требуется помощь — выкопать яму под дерево на участке. Земля плотная, инструмент есть. Работа примерно на 2 часа. Оплата — 6000. Извините, если пишу не вовремя",
            "Ответ": {"explanation": "Нет ничего подходящего", "is_relevant": "False"}
        },
        {
            "Сообщение": "Да я вообще не знаю, что в этот диплом писать",
            "Ответ": {"explanation": "Можно предложить помощь с дипломом", "is_relevant": "True"}
        }

    ]
"""

def check_message_relevancy_with_llm(client, msg):

    response = client.responses.create(
        model="gpt-5-nano-2025-08-07",
        reasoning={ "effort": "medium" },
        text={
                "verbosity": "low",
                "format": {
                    "type": "json_schema",
                    "name": "MsgRelevancy",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "explanation": {"type": "string"},
                            "is_relevant": {"type": "boolean"}
                        },
                        "required": ["explanation", "is_relevant"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
        input=[
            {
                "role": "developer",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": msg
            }
        ],
    )

    return response.output_text

def parse_json(text):
    parsed_json = None
    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
    return parsed_json


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
        if response.get("is_relevant") == msg.get("is_relevant"):
            correct_tests += 1
        else:
            print(msg.get("msg"))
            print(response)
    
    print(f"Correct tests: {correct_tests}/{num_tests}")
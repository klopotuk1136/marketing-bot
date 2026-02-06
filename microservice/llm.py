from typing import Any, Dict, List
from openai import OpenAI
from pydantic import BaseModel
import json

def get_openai_client(openai_api_key):
    client = OpenAI(api_key=openai_api_key, base_url="https://api.deepseek.com")
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
EXAMPLE INPUT:
кто может сделать задание для проекта (маркетинг)срочно
        
EXAMPLE JSON OUTPUT:
    {"reason": "Человеку нужно сделать задание", "is_relevant": "True"}

EXAMPLE INPUT:
Привет. Кто может сделать работу по "Введение в Data Science и искуственный интеллект"? Необходимо построить несколько моделей машинного/глубокого обучения с построением графиков для анализа базы данных. По цене договоримся, но деньгам я не обижу
        
EXAMPLE JSON OUTPUT:
    {"reason": "Человеку нужно сделать работу", "is_relevant": "True"}

EXAMPLE INPUT:
Здравствуйте. Требуется помощь — выкопать яму под дерево на участке. Земля плотная, инструмент есть. Работа примерно на 2 часа. Оплата — 6000. Извините, если пишу не вовремя
        
EXAMPLE JSON OUTPUT:
    {"reason": "Нет ничего подходящего", "is_relevant": "False"}

EXAMPLE INPUT:
Да я вообще не знаю, что в этот диплом писать
        
EXAMPLE JSON OUTPUT:
    {"reason": "Можно предложить помощь с дипломом", "is_relevant": "True"}
"""

# Добавить кусок про не пропускание чужой рекламы


def check_message_relevancy_with_llm(client, msg):

    response = client.chat.completions.create(
        model="deepseek-chat",
        response_format={
            'type': 'json_object'
        },
        messages =[
            {
                "role": "system",
                "content": system_prompt
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
import json
import uuid

import requests
from fastapi import FastAPI
from fastapi.params import Body
from fastapi import BackgroundTasks

from openai import chat
from parse_wexin_paper import get_paper_content

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


def get_tenant_access_token():
    url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
    body = {

        "app_id": "cli_xxx",  # todo 可以将其放入环境变量中，不能泄漏！！！！
        "app_secret": "jwxxx"  # todo 可以将其放入环境变量中，不能泄漏！！！！
    }
    res = requests.post(url, json=body)
    return res.json().get('tenant_access_token')


def send_response(message_id, text_content):
    # 回复消息
    url = f'https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply'
    res_content = {
        "text": text_content
    }
    response = {
        "content": json.dumps(res_content),
        "msg_type": "text",
        "uuid": str(uuid.uuid4())
    }
    token = get_tenant_access_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': f'application/json; charset=utf-8'
    }
    print(f'response url:{url}, header:{headers}, data:{response}')
    requests.post(url, headers=headers, json=response)


def handle_task(payload):
    # 用户发过来的消息
    content = payload.get('event').get('message').get('content')
    print(f'content:{content}')
    # 获取文章内容
    paper_content = get_paper_content(json.loads(content).get('text'))
    prompt = f"""我会给你一篇由<<begin>>和<<end>>包含的文章，请完成如下任务：
    1.总结一下文章，以列表的形式输出关键要点，保持语句通顺，简单易懂。
    2.分析文章中是否有逻辑问题，如果有请依次列出问题，写在下面的【逻辑问题列表】中，没有则保持空。
    3.分析文章中是否有诱导读者购买课程、商品等行为，如果有请写在下面的【诱导购买列表】中，没有则保持空。
    4.分析文章中是否有焦虑制造倾向，如果有请写在下面的【焦虑制造列表】中，没有则保持空。

    严格按照如下格式输出：
    【总结】
    这里放总结内容。
    【逻辑问题列表】
    在这里列出逻辑问题。
    【诱导购买列表】
    在这里列出诱导购买内容。
    【焦虑制造列表】
    在这里放焦虑制造内容。

    这是文章：
    <<begin>>
    {paper_content}
    <<end>>"""
    print(f'prompt:{prompt}')
    # 调用ChatGPT进行总结
    summary = chat(prompt)
    message_id = payload.get('event').get('message').get('message_id')
    # 回复消息
    send_response(message_id, summary)


@app.post("/")
async def say_hello(background_tasks: BackgroundTasks, payload: dict = Body(...)):
    # 检测到CHALLENGE标记就直接返回，以通过飞书的接入
    challenge = payload.get('CHALLENGE')
    if challenge:
        print(f'CHALLENGE flag is exist, return it.')
        return payload
    # print(f'payload:{json.dumps(payload)}')
    # feishu要求1秒内返回，所以此处起一个后台任务处理
    background_tasks.add_task(handle_task, payload)
    print('###### i will return immediately。。。')
    return ''


if __name__ == '__main__':
    get_tenant_access_token()

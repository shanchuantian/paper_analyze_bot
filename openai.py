import requests

url = "https://openai.api2d.net/v1/chat/completions"

headers = {
  'Content-Type': 'application/json',
    # todo 不能泄漏
  'Authorization': 'Bearer fkxxx' # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格。
}


def chat(content, role='user', model='gpt-3.5-turbo'):
    data = {
      "model": model,
      "messages": [{"role": role, "content": content}]
    }
    print('start chat to chatgpt....')
    response = requests.post(url, headers=headers, json=data)
    print("ChatGPT Status Code", response.status_code)
    print("ChatGPT JSON Response ", response.json())
    return response.json().get('choices')[0].get('message').get('content')

if __name__ == '__main__':
    content = '你好'
    chat(content=content)
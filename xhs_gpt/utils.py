import requests
from langchain.tools import Tool


def sign(uri, data=None, a1="", web_session=""):
    # 填写自己的 flask 签名服务端口地址
    res = requests.post("http://localhost:5005/sign",
                        json={"uri": uri, "data": data, "a1": a1, "web_session": web_session})
    signs = res.json()
    return {
        "x-s": signs["x-s"],
        "x-t": signs["x-t"]
    }

def unzip_prompt_run(tools):
    return [i.tool for i in tools],[Tool.from_function(func=i.run, name=i.tool['name'], description=i.tool['description']) for i in tools]
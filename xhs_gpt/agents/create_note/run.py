import datetime
import json
import qrcode
from time import sleep

import requests
from langchain.chat_models import ChatOpenAI
from operator import itemgetter
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda

from xhs import XhsClient, DataFetchError
from playwright.sync_api import sync_playwright
import tempfile
from PIL import Image, ImageTk
import tkinter as tk

class GenerateQRCode:
    tool = {
        "name": "generate_login_qrcode",
        "description": "Generate a qrcode for login. Response with the string path to the qrcode image, the `qr_id` and `qr_code`.",
        "parameters": {"type": "object",
                       "properties": {
                       }
                       }
    }

    @classmethod
    def run(cls,):
        ...
json_llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106").bind(response_format={ "type": "json_object" })
create_note_body_prompt = ChatPromptTemplate([
    ('system',"""User will provide you with a topic. You need to generate a Xiaohongshu post for the topic in JSON. The post contains a title, a description, a list of tags and a list of image_descriptions.
    
Users in Xiaohongshu use certain writing styles:

1. Friendly and Casual: Posts on Xiaohongshu are typically written in the first person, creating a feeling of sharing between friends. The language is colloquial and down-to-earth, making it approachable and relatable.

2. Rich in Visual Content: Xiaohongshu posts often come with numerous pictures, which are closely integrated with the text content, making the information more intuitive and understandable.

3. Use of Emoji: Xiaohongshu posts frequently use emojis to enrich expression and add fun, making the content more lively and engaging.

4. Diverse Topics: Xiaohongshu covers a variety of topics, such as beauty, food, travel, lifestyle, etc. Therefore, its writing style is also very diverse, including detailed product reviews and relaxed life sharing.

5. High Interactivity: Xiaohongshu posts usually encourage readers to participate in discussions, for example by asking questions or initiating topics, enhancing the interactivity of the posts.

6. Practicality: Xiaohongshu posts often provide practical information, such as product use experiences, travel strategies, etc. These pieces of information are based on personal actual experiences and have high reference value.

# Xiaohong JSON post Examples
```json
{{"title": "绝了❗️为“哄”孩子喝光牛奶，设计师有妙招👏", 
"description": "近年来，日本学校午餐牛奶剩余问题已成为小学和初中难以解决的问题。因此。奥美日本为Seki Milk重新设计了包装：将漫画用白色的笔印刻在瓶身之上，若想看完漫画内容，就必须把整瓶牛奶干光！\n这是一个独特的想法，并得到了很多回应。牛奶瓶上画的是漫画家阿美明彦的原创作品《牛奶怪物》，总共多达10集。\n该牛奶在岐阜县关市旭丘小学的学校午餐时间试用时，孩子们的反应都非常好，有些小朋友说：“漫画很有趣，学校的午餐也变得有趣！”", 
"tags": ["工业设计", "设计灵感", "产品设计", "漫画", "设计", "牛奶", "牛奶瓶", "包装设计"], 
"image_descriptions": ["牛奶瓶上印有漫画《牛奶怪物》的设计", "设计师为Seki Milk重新设计的牛奶包装"] }}
```
```json
{{"title": "158/102 来看小狗流鼻涕", 
"description": "衣服上的狗狗太可爱了💧", 
"tags": ["今天穿什么香", "狗狗t", "白短裤", "小个子穿搭"], 
"image_descriptions": ["衣服上有可爱的狗狗图案"] }}
{{"title": "这种又粘人又帅的混血帅哥到底是谁在谈啊", 
"description": "原来是我自己", 
"tags": ["姐弟恋", "异国恋", "混血", "小奶狗", "外国男友", "男朋友", "恋爱", "恋爱日常", "甜甜的恋爱", "情侣", "小情侣的日常", "日常碎片PLOG", "笔记灵感"], 
"image_descriptions": ["混血帅哥自拍"] }}
```
```json
{{"title": "🍁来Arrow Town赏秋", 
"description": "深秋的箭镇好治愈，漫山遍野的秋色，仿佛打翻了颜料盘🎨，来了箭镇要好好拍照记录📝。\n\n📷拍照点：1⃣️Wilcox Green：Wilcox Green是个拍照标志地，最佳拍照时间在下午四点左右，但是容易发生在你拍照的时候，旁边等着很多游客，这时候只能尴尬地笑笑，表情管理有点难😅\n2⃣️箭镇大草坪：Wilcox Green所在的大草坪，选一处人少的地方拍照片，这时候怎么凹造型都没人催\n3⃣️街景：在箭镇，拍拍Buckingham Street和Arrow Lane的街景和建筑也不错，可多走两步到Wiltshire Street找个高点往下拍五彩树林和街景\nps：找到一段在施工的路，我在保证安全的前提下坐在地上拍了一张，但不推荐。\n\n箭镇每年赏秋最佳季节是四月中旬到五月初，四月最后一周会举办金秋节，这个季节这边时有阵雨🌦️，但是阴雨天的箭镇也有不一样的感觉，这次在箭镇我全程用富士相机📷，适配指数💯", 
"tags": ["五一去哪玩", "新西兰", "新西兰箭镇", "和大自然亲密接触", "治愈系风景", "富士相机"], 
"image_descriptions": ["Arrow Townm Wilcox Green下午四点左右，在你拍照的时候旁边等着很多游客", "箭镇大草坪：Wilcox Green所在的大草坪，人少，凹造型","Buckingham Street和Arrow Lane的街景和建筑, 施工的路"] }}
```
```json
{{"title": "五一出游好去处｜洞头岛屿生活市集", 
"description": "刚从南京回来\n陪我回来的闺蜜问我去哪里玩\n这不赶巧了\n洞头刚好有台湾美食节！\n不只是美食\n还有精彩的舞台演出！\n\n网红打卡大黄鸭\n台湾美食一条gai\n免费啤酒畅饮\n精彩的乐队演出\n氛围感落日灯……\n真的又好出片\n又快乐……\n\n🕒4.29～5.3 17:00～21:00\n📍洞头北岙街道东沙渔港", 
"tags": ["温州探店", "洞头旅游攻略", "洞头旅游", "五一去哪儿"], 
"image_descriptions": ["网红打卡大黄鸭", "台湾美食一条gai", "免费啤酒畅饮", "精彩的乐队演出", "氛围感落日灯"] }}
```

Always response in JSON."""),
    ('human', "{input}"),
])
create_note_body_chain = {'input': itemgetter('topic')} | create_note_body_prompt | json_llm | StrOutputParser() | RunnableLambda(json.loads)

def create_image(desc):
    response = openai.images.generate(
        prompt=desc,
        model='dall-e-3',
    )
    return response.data[0].url
class CreateNote:
    tool = {
        "name": "create_note",
        "description": "Create a post on Xiaohongshu.",
        "parameters": {"type": "object",
                       "properties": {
                           "topic":{
                               "type":"string",
                               "description":"The topic of the post"
                           },
                           "token_file": {
                               "type": "string",
                               "description": "path to token file"
                           },
                       }
                       }
    }

    @classmethod
    def run(cls, topic, token_file):
        from xhs_gpt.utils import sign
        note_body = create_note_body_chain.invoke({'topic':topic})
        images = []
        for desc in note_body['image_descriptions']:
            image_url = create_image(desc)
            with tempfile.NamedTemporaryFile('wb', delete=False) as f:
                f.write(requests.get(image_url).content)
                images.append(f.name)
        with open(token_file,'r') as f:
            cookie = f.read()
        xhs_client = XhsClient(cookie=cookie,sign=sign)

        note = xhs_client.create_image_note(note_body['title'], note_body['description'], images, is_private=True, post_time=datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
        return note



from langchain.utilities.dalle_image_generator import DallEAPIWrapper
import openai
openai.Image
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI

llm = OpenAI(temperature=0.9)
prompt = PromptTemplate(
    input_variables=["image_desc"],
    template="Generate a detailed prompt to generate an image based on the following description: {image_desc}",
)
chain = LLMChain(llm=llm, prompt=prompt)

class CreateNoteBody:
    tool = {
        "name": "create_note_body",
        "description": "Generate the body of a note.",
        "parameters": {"type": "object",
                       "properties": {
                       }
                       }
    }

    def run(self):
        pass

def test_create_note_with_ats_topics(xhs_client: XhsClient):
    title = "我是通过自动发布脚本发送的笔记"
    desc = "deployed by GitHub xhs， #Python[话题]# @ReaJason"
    files = [
        "/Users/reajason/Downloads/221686462282_.pic.png",
    ]

    # 可以通过 xhs_client.get_suggest_ats(ats_keyword) 接口获取用户数据
    ats = [
        {"nickname": "ReaJason", "user_id": "63273a77000000002303cc9b", "name": "ReaJason"}
    ]

    # 可以通过 xhs_client.get_suggest_topic(topic_keyword) 接口获取标签数据
    topics = [
        {
            "id": "5d35dd9b000000000e0088dc", "name": "Python", "type": "topic",
            "link": "https://www.xiaohongshu.com/page/topics/5d35dd9ba059940001703e38?naviHidden=yes"
        }
    ]
    note = xhs_client.create_image_note(title, desc, files, ats=ats, topics=topics, is_private=True,
                                        post_time="2023-07-25 23:59:59")
    beauty_print(note)


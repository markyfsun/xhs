
from openai import OpenAI
from xhs import XhsClient


class GetNote:
    tool = {
        "name": "get_note",
        "description": "Get a specific note on Xiaohongshu. Require login.",
        "parameters": {"type": "object",
                       "properties": {
                           "note_id": {
                               "type": "string",
                               "description": "id of the specific note"
                           },
                           "token_file": {
                               "type": "string",
                               "description": "path to token file"
                           },
                       },
                       'required':['id',]
                       }
    }

    @classmethod
    def run(cls, note_id, token_file):
        from xhs_gpt.utils import sign
        with open(token_file, 'r') as f:
            cookie = f.read()
        xhs_client = XhsClient(cookie=cookie, sign=sign)
        note = xhs_client.get_note_by_id(note_id)
        return summary_note(note)


def summary_note(note:dict):
    text = f"""{note["title"]}
    
    {note['desc']}

    tags: {[i['name'] for i in note['tag_list']]}"""
    image_urls = [i['info_list'][0]['url'] for i in note['image_list']]

    client = OpenAI()
    content = [{"type": "text", "text": text}]
    content += [
        {
            "type": "image_url",
            "image_url": {
                "url": i,
            },
        } for i in image_urls
    ]
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role":"system","content":"User will display images and text from a post on Xiaohongshu platform in China. First beifly summarize the post, then conclude with features of this post. Also mention the punchline if it has one."},
            {
                "role": "user",
                "content": content
            }
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content

s=GetNote.run('6504357800000000130346ae','/var/folders/k9/2mh_kjcd0cqg6nbz0wxy988r0000gn/T/xhs_login_4n6xz79l.cookie')
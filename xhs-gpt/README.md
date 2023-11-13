# xhs-gpt

Let ChatGPT login, view notes, write and post notes with your Xiaohongshu account.

## Installation

First install all requirements for `xhs`, then install `xhs-gpt` in editable mode.  

Install `xhs` following the [document](https://reajason.github.io/xhs/basic).
```bash
pip install xhs # 下载 xhs 包

pip install playwright # 下载 playwright

playwright install

docker run -it -d -p 5005:5005 reajason/xhs-api:latest
```

Install `xhs-gpt` in editable mode.
```bash
cd xhs-gpt
# poetry install
pip install -e .  # install xhs-gpt requirements
```

## Launch LangServe

```bash
# cd xhs-gpt
langchain serve
```

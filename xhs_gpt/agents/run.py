from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.agent import AgentAction, AgentFinish, AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool

from xhs_gpt.agents.get_feed.run import GetFeed
from xhs_gpt.agents.get_note.run import GetNote
from xhs_gpt.agents.login import Login
from xhs_gpt.agents.create_note.run import CreateNote
from xhs_gpt.utils import unzip_prompt_run

xhs_tool_prompts, xhs_tool_runs = unzip_prompt_run([
    Login,
    CreateNote,
    GetFeed,
    GetNote,
])

xhs_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a Xiaohongshu Assistant. Fulfill user requirements using given tools.
Pay attention the dependency relation among them, some tools may require the output of others."""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm = ChatOpenAI(temperature=.3, model="gpt-4-1106-preview")
xhs_llm = llm.bind(functions=xhs_tool_prompts)
xhs_agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_functions(
                x["intermediate_steps"]
            ),
        }
        | xhs_agent_prompt
        | xhs_llm
        | OpenAIFunctionsAgentOutputParser()
)

xhs_agent_executor = AgentExecutor(
    agent=xhs_agent, tools=xhs_tool_runs, max_iterations=10, early_stopping_method="generate", return_intermediate_steps=True,
    verbose=True
)

if __name__ == '__main__':
    result = xhs_agent_executor.invoke({'input':'分析游戏主题中最受欢迎的一篇笔记，针对其内容发表一篇笔记。token_file:`/tmp/xhs_login_70dszwmw.cookie`'})
    print(result['output'])
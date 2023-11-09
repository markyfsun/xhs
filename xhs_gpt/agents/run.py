from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents.agent import AgentAction, AgentFinish, AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from xhs_gpt.agents.login import Login
from xhs_gpt.agents.create_note.run import CreateNote
from xhs_gpt.utils import unzip_prompt_run

xhs_tool_prompts, xhs_tool_runs = unzip_prompt_run([
    CreateNote,
    Login,
])

xhs_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a Xiaohongshu Assistant."""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")
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
    result = xhs_agent_executor.invoke({'input':'帮我发一篇关于可爱狗狗的帖子'})
import sys
import os
from dotenv import load_dotenv
import asyncio
from tools.retrieve import retrieve
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate

async def query_or_respond(messages:list):
      llm = init_chat_model("mistral-large-latest", model_provider="mistralai")
      llm_with_tools = llm.bind_tools([retrieve])
      response=await llm_with_tools.ainvoke(messages)
      try:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
      except (IndexError, KeyError, TypeError):
        tool_call = tool_name = tool_args = None
        # Use your tool
      if tool_name == "retrieve":
        result = retrieve(tool_args["query"])  # your actual tool function

        # Add the tool result
        messages.append(response)  # the AIMessage with the tool call
        messages.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )
      usedRAG=False
    #   print(messages)
      for message in reversed(messages):
        if isinstance(message, ToolMessage):
            # print(5)
            last_tool_message=message
            # print(last_tool_message,messages)
            usedRAG=True
            break
      if usedRAG:
            prompt2 = f"""Based on the following context and conversation history, 
            please provide a relevant and contextual response. If the answer cannot 
            be derived from the context, then use ur general knowledge

            Context from documents:
            {last_tool_message}

            Previous conversation:
            {messages} """

            final_message=await llm_with_tools.ainvoke(prompt2)
            # print(1)

            return final_message.content
    #   print(2)
      return response.content

async def main():
    load_dotenv()

    langsmith_tracing = os.getenv("LANGSMITH_TRACING")
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    mistral_api_key = os.getenv("MISTRAL_API_KEY")

    system_message = SystemMessage(content="""
    You are a helpful assistant.

    If you are confident that you know the answer, reply directly to the user.

    However, if you are not confident or lack context, use the `retrieve` tool to fetch relevant information before answering. Use the tool when the user's question seems ambiguous, references unknown topics, or asks for specific content like "figures", "activities", or "sections".
    """)

    user_message = HumanMessage(content="ok can you tell about the five great debates from the retrieve tool?")

    messages = [
        system_message,user_message
    ]

    print(await query_or_respond(messages))


            
    
      














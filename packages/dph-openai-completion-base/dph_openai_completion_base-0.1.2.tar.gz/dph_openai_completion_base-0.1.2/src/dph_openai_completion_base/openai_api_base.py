from .assistant_response import AssistantResponse
from .openai_db_connector_base import OpenAIDBConnectorBase
from openai import AsyncOpenAI
import json
import time

class OpenAIApiBase():
    def __init__(self,
                 mode,
                 logger,
                 db_connector: OpenAIDBConnectorBase,
                 prompt,
                 functions,
                 temperature,
                 model,
                 top_p,
                 skip_functions_list,
                 response_format,
                 openai_api_key,
                 vector_store_max_results,
                 callback_factory = None,
                 max_consecutive_tool_calls = 100
                 ):
                    self.mode = mode
                    self.logger = logger
                    self.db_connector = db_connector
                    self.prompt = prompt
                    self.functions = functions
                    self.temperature = temperature
                    self.model = model
                    self.top_p = top_p
                    self.response_format = response_format
                    self.skip_functions_list = skip_functions_list
                    self.vector_store_max_results = vector_store_max_results
                    self.callback_factory = callback_factory

                    self.openai_client_beta = AsyncOpenAI(api_key=openai_api_key).beta
                    self.openai_client = AsyncOpenAI(api_key=openai_api_key)

                    self.max_consecutive_tool_calls = 100


    def _get_called_functions(self, tools) -> dict:
        called_functions = {}

        for tool in tools:
            called_functions[tool.function.name] = tool.function
            self.logger.info(f'FUNCTION CALL {tool.function.name} called with args: {tool.function.arguments}')
        return called_functions

    async def _process_function_call_results(self, tool_calls, thread_id: str):
        all_function_names = []
        for tool_call in tool_calls:
            all_function_names.append(tool_call.function.name)

        skip_list = self.skip_functions_list

        for tool_call in tool_calls:
            func_args = tool_call.function.parsed_arguments
            func_name = tool_call.function.name

            skip = False
            for base_function_name in skip_list:
                if base_function_name in all_function_names and func_name in skip_list[base_function_name]:
                    skip = True
            if skip:
                self.logger.info(f'FUNCTION CALL RESULT {func_name} in thread {thread_id}: SKIP FUNCTION CALL')
                continue

            msg = {
                'role': 'assistant',
                'content': None,
                'function_call': {
                    'name': func_name,
                    'arguments': json.dumps(func_args),
                }
            }
            await self._append_chat_completion_history(thread_id, msg)

            callback_handler = self.callback_factory.make(func_name, thread_id)
            out = await callback_handler.process(func_args)

            msg = {
                'role': 'function',
                'name': func_name,
                'content': out
            }
            self.logger.info(f'FUNCTION CALL RESULT {func_name} in thread {thread_id}: {out}')
            await self._append_chat_completion_history(thread_id, msg)

        return self._get_called_functions(tool_calls)

    async def create_message(self, thread_id: str, content: str, role: str = 'user'):
        history = await self.db_connector.get_chat_completion_history(thread_id)
        if len(history) == 0:
            await self._append_chat_completion_history(thread_id, {"role": "system", "content": self.prompt})

        message = {
            'role': role,
            'content': content,
        }
        history = await self._append_chat_completion_history(thread_id, message)
        return str(len(history))

    async def query_vector_store(self, query):
        vector_store_id = await self.db_connector.get_vector_store_id()

        data = await self.openai_client.vector_stores.search(
            vector_store_id=vector_store_id,
            query=query,
            max_num_results=self.vector_store_max_results
        )
        result = []
        for row in data:
            row_type, row_data = row
            if row_type != 'data':
                continue
            for content in row_data:
                score = content.score
                content = content.content

                for content_entry in content:
                    result.append({
                        'text': content_entry.text,
                        'score': score,
                    })
        return result

    def _parse_db_history(self, history: list):
        result = []
        for row in history:
            result.append(row['message'])
        return result

    async def _append_chat_completion_history(self, thread_id: str, message: dict):
        history = await self.db_connector.get_chat_completion_history(thread_id)
        history.append({'message': message, 'timestamp': time.time()})
        await self.db_connector.set_chat_completion_history(thread_id, history)
        return history

    async def run_stream(self, thread_id, tool_choice: str = "auto"):

        functions = []

        if tool_choice != "none":
            functions = self.functions

        called_functions = {}
        for i in range(1, self.max_consecutive_tool_calls):
            if i == self.max_consecutive_tool_calls - 1:
                raise Exception(f'Too many consecutive tool calls in thread {thread_id}')

            history = self._parse_db_history(await self.db_connector.get_chat_completion_history(thread_id))

            completion = await self.openai_client_beta.chat.completions.parse(
                messages=history,
                model=self.model,
                response_format=self.response_format,
                temperature=self.temperature,
                top_p=self.top_p,
                tools=functions,
                user=thread_id  # to prevent tokens caching between different chats (can cause answers in russian)
            )
            self.logger.info(completion)
            tool_calls = completion.choices[0].message.tool_calls
            if tool_calls is None:
                break
            called_functions = await self._process_function_call_results(tool_calls, thread_id)

        result_msg = completion.choices[0].message
        content_raw = None
        if hasattr(result_msg, 'content'):
            content_raw = result_msg.content
            result_msg.content = result_msg.content.strip()
            content = result_msg.content
            try:
                content = content.splitlines()[0]
                parsed_content = json.loads(content)
                if 'response_text' in parsed_content:
                    msg = {
                        'role': 'assistant',
                        'content': parsed_content['response_text']
                    }
                    await self._append_chat_completion_history(thread_id, msg)
            except Exception as e:
                self.logger.error(f'ERROR PARSING JSON in openai_completion_api: {content}')

        return AssistantResponse(final_response_str=content_raw, called_functions=called_functions)
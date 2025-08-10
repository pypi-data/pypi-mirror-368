"""wrap all language model apis - use REST direct to avoid deps in the library
This is a first draft - will map this to lean more on the database model 
"""

import requests
import json
import os
import typing
from .CallingContext import CallingContext
from percolate.models import MessageStack
from percolate.services import PostgresService
from percolate.models.p8 import AIResponse
import uuid
from percolate.utils import logger
import traceback
from .MessageStackFormatter import MessageStackFormatter
from .utils import *


ANTHROPIC_MAX_TOKENS_IN = 8192

class OpenAIResponseScheme(AIResponse):
    @classmethod
    def parse(cls, response:requests.models.Response, sid: str,  model_name:str, streaming_callback:typing.Callable=False)->AIResponse:
        """
        parse the response into our canonical format - if streaming callback send to print
        
        example tool call response
        ```
        'tool_calls': [{'id': 'call_0KPgsQaaso8IXPUpG6ktM1DC',
        'type': 'function',
        'function': {'name': 'get_weather',
            'arguments': '{"city":"Dublin","date":"2023-10-07"}'}}],
        ```
        """
        def adapt(t):
                """we want something we can call and also something to construct the message that is needed for the tool call"""
                f = t['function']
                return   {'name': f['name'], 'arguments':f['arguments'], 'id': t['id']} 
            
        try:
            if streaming_callback:
                logger.debug(f"Streaming response")
                response = stream_openai_response(response,printer=streaming_callback)
            else:
                response = response.json()
            
           
            if response.get('error'):
                logger.warning(f"Error response {response['error'].get('message')}")
                return AIResponse(id = str(uuid.uuid1()),model_name=model_name, tokens_in=0,tokens_out=0, role='assistant',
                                session_id=sid, content=response['error'].get('message'), status = 'ERROR')
            choice = response['choices'][0]
            tool_calls = choice['message'].get('tool_calls') or []
            tool_calls = [adapt(t) for t in tool_calls]
            
            return AIResponse(id = str(uuid.uuid1()),
                    model_name=response['model'],
                    tokens_in=response['usage']['prompt_tokens'],
                    tokens_out=response['usage']['completion_tokens'],
                    session_id=sid,
                    verbatim=choice['message'],
                    role=choice['message']['role'],
                    content=choice['message'].get('content') or '',
                    status='RESPONSE' if not tool_calls else "TOOL_CALLS",
                    tool_calls=tool_calls)
        except Exception as ex:
            logger.warning(f"unexpected structure in OpenAI scheme message {response=} - caused the error {ex}")
            raise 
                    
class AnthropicAIResponseScheme(AIResponse):
    @classmethod
    def parse(cls, response:requests.models.Response, sid: str,  model_name:str, streaming_callback:typing.Callable=False )->AIResponse:
        """parse the response into our canonical format - if streaming callback send to print"""
        if streaming_callback:
            response = stream_anthropic_response(response,printer=streaming_callback)
        else:
            response = response.json()
        choice = response.get('content') or []
        def adapt(t):
            """anthropic map to our interface"""
            return {'name': t['name'], 'arguments':t['input'], 'id': t['id'], 'scheme': 'anthropic'}
        verbatim = [t for t in choice if t['type'] == 'tool_use']
        tool_calls = [adapt(t) for t in verbatim]
        if verbatim:
            """when tools are used we need a verbatim message with tool call??"""
            verbatim = {
                'role': response['role'],
                'content': response['content']
            }
        
        content = "\n".join([t['text'] for t in choice if t['type'] == 'text']) 
        return AIResponse(id = str(uuid.uuid1()),
                model_name=response['model'],
                tokens_in=response['usage']['input_tokens'],
                tokens_out=response['usage']['output_tokens'],
                session_id=sid,
                role=response['role'],
                content=content or '',
                verbatim=verbatim ,
                status='RESPONSE' if not tool_calls else "TOOL_CALLS",
                tool_calls=tool_calls)
        
class GoogleAIResponseScheme(AIResponse):
    @classmethod
    def parse(cls, response:requests.models.Response, sid: str, model_name:str, streaming_callback:typing.Callable=False)->AIResponse:
        """parse the response into our canonical format - if streaming callback send to print"""
        if streaming_callback:
            response = stream_google_response(response,printer=streaming_callback)
        else:
            response= response.json()
        message = response['candidates'][0]['content']
        choice = message['parts']
        content_elements = [p['text'] for p in choice if p.get('text')]
        def adapt(t):
            return {'function': {'name': t['name'], 'arguments':t['args'], 'id': t['name'],'scheme': 'google'}}
        tool_calls = [adapt(p['functionCall']) for p in choice if p.get('functionCall')]
        tool_calls = [t['function'] for t in tool_calls]
        return AIResponse(id = str(uuid.uuid1()),
                model_name=model_name, #does not seem to return it which is fair
                tokens_in=response['usageMetadata']['promptTokenCount'],
                tokens_out=response['usageMetadata']['candidatesTokenCount'],
                session_id=sid,
                role=message['role'],
                content=',\n'.join(content_elements),
                verbatim=message if tool_calls else None,
                status='RESPONSE' if not tool_calls else "TOOL_CALLS",
                tool_calls=tool_calls)

def try_get_open_ai_key():
    """
    for now we default to open ai keys for many types of models e.g. whisper or embeddings but we could generally use this to load other keys but we need to flesh out the abstraction
    """
    db = PostgresService()
    
    try:
        params = db.execute("""select token from p8."LanguageModelApi" where token_env_key = 'OPENAI_API_KEY' and token is not null limit 1""")
        if params:
            return params[0]['token']
    except:
        logger.warning(f"failed to get the open ai key - {traceback.format_exc()}")        
    

class LanguageModel:
    """the simplest language model wrapper we can make"""
    def __init__(self, model_name:str):
        """"""
        self.model_name = model_name
        self.db = PostgresService()
        #TODO we can use a cache for this in future
        self.params = self.db.execute('select * from p8."LanguageModelApi" where name = %s ', (model_name,))
        if not self.params:
            raise Exception(f"The model {model_name} does not exist in the Percolate settings")
        self.params = self.params[0]
        
        if self.params['token'] is None:
            """if the token is not stored in the database we use whatever token env key to try and load it from environment"""
            self.params['token'] = os.environ.get(self.params['token_env_key'])
            if not self.params['token']:
                raise Exception(f"There is no token or token key configured for model {self.model_name} - you should add an entry to Percolate for the model using the examples in p8.LanguageModelApi")
        """we use the env in favour of what is in the store"""
        env_token = os.environ.get(self.params['token_env_key'])
        self.params['token'] = env_token  if env_token is not None and len(env_token) else self.params.get('token')
        self._scheme = self.params.get('scheme','openai')
        
    def parse(self, response: requests.models.Response | typing.Any, context: CallingContext=None) -> AIResponse:
        """the llm response or HybridResponse from streaming is parsed into our canonical AIResponse.
        this is also done inside the database and here we replicate the interface before dumping and returning to the executor
        """
 
        streaming_callback = context.streaming_callback if context and context.streaming_callback else None

        try:
            if response.status_code not in [200,201]:
                logger.warning(f"There was an error requesting - {response.content}")
                pass #do something for errors
 
            sid = None if not context else context.session_id
            """check the HTTP response first"""
            if self.params.get('scheme') == 'google':
                return GoogleAIResponseScheme.parse(response, sid=sid, model_name=self.model_name,streaming_callback=streaming_callback)
            if self.params.get('scheme') == 'anthropic':
                return AnthropicAIResponseScheme.parse(response,sid=sid,model_name=self.model_name,streaming_callback=streaming_callback)
            return OpenAIResponseScheme.parse(response,sid=sid, model_name=self.model_name,streaming_callback=streaming_callback)
        except Exception as ex:
            logger.warning(f"failing to parse {response} {traceback.format_exc()}")
            raise
        
    def __call__(self, messages: MessageStack, functions: typing.List[dict], context: CallingContext=None, debug_response:bool=False ) -> AIResponse:
        """call the language model with the message stack and functions.
        We return the parsed response unless the caller asks for the raw
        We support a hybrid mode of return the content stream and holding the function call
        """
            
        try:
            response = self._call_raw(messages=messages, functions=functions,context=context)
            
            logger.debug(f"{response=}, {context=}")
            if debug_response:
                return response
            
       
            
            """for consistency with DB we should audit here and also format the message the same with tool calls etc."""
            response = self.parse(response,context=context)
            return response
        except:
            # data = {
            #     'messages': messages,
            #     'functions': functions,
            #     'context': context
            # }
            
            # import pickle
            # with open('/tmp/p8dump', "wb") as f:
            #     pickle.dump(data, f)
            
            # print('dumped', '/tmp/p8dump')
            raise
    
    def ask(self, question:str, functions: typing.List[dict]=None, system_prompt: str=None,context: CallingContext=None, **kwargs):
        """simple check frr question. our interface normally uses MessageStack and this is a more generic way
        
        If you want to stream create a context 
        Args:
            question: any question
            system_prompt: to test altering model output behaviour
            functions: optional list of functions in the OpenAPI like scheme
        """
        return self.__call__(MessageStack(question,system_prompt=system_prompt), functions=functions, context=context, **kwargs)
        
        
    def _call_raw(self, messages: MessageStack, functions: typing.List[dict], context: CallingContext=None):
         """the raw api call exists for testing - normally for consistency with the database we use a different interface"""
   
         return self.call_api_simple(messages.question, 
                                    functions=functions,
                                    system_prompt=messages.system_prompt, 
                                    data_content=messages.data,
                                    is_streaming=(context and context.is_streaming))

    @classmethod 
    def from_context(cls, context: CallingContext) -> "LanguageModel":
        return LanguageModel(model_name=context.model)
        
    def get_embedding(self, text: str) -> typing.List[float]:
        """Get embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        from percolate.utils.embedding import get_embedding
        
        # Use the embedding utility with our model settings
        scheme = self.params.get('scheme', 'openai')
        model = self.params.get('embedding_model', self.model_name)
        
        return get_embedding(
            text=text,
            model=model,
            api_key=self.params['token'],
            scheme=scheme
        )
        
    def get_embeddings(self, texts: typing.List[str]) -> typing.List[typing.List[float]]:
        """Get embeddings for multiple texts in batch
        
        This is much more efficient than calling get_embedding multiple times
        as it batches the requests to the embedding provider.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        from percolate.utils.embedding import get_embeddings
        
        # Use the embedding utility with our model settings
        scheme = self.params.get('scheme', 'openai')
        model = self.params.get('embedding_model', self.model_name)
        
        return get_embeddings(
            texts=texts,
            model=model,
            api_key=self.params['token'],
            scheme=scheme
        )
    
      
    def _elevate_functions_to_tools(self, functions: typing.List[dict]):
        """dialect of function wrapper for openai scheme tools"""
        return [{'type': 'function', 'function': f} for f in functions or []]
          
    def _adapt_tools_for_anthropic(self, functions: typing.List[dict]):
        """slightly different dialect of function wrapper - rename parameters to input_schema"""
        def _rewrite(d):
            return {
                'name' : d['name'],
                'input_schema': d['parameters'],
                'description': d['description']
            }
 
        return [_rewrite(d) for d in functions or []]
    
    def call_api_simple(self, 
                        question:str, 
                        functions: typing.List[dict]=None, 
                        system_prompt:str=None, 
                        data_content:typing.List[dict]=None,
                        is_streaming:bool = False,
                        temperature: float = 0.0,
                        **kwargs):
        """
        Simple REST wrapper to use with any language model
        """
        logger.debug(f"invoking model {self.model_name}, {is_streaming=}")
        """select this from the database or other lookup
        e.g. db.execute('select * from "LanguageModelApi" where name = %s ', ('gpt-4o-mini',))[0]
        """
        params = self.params
        data_content = data_content or []
        
        """we may need to adapt this e.g. for the open ai scheme"""
        tools = functions or None
      
        url = params["completions_uri"]
        """use the env first"""
         
        token = params['token']
        if not token or len(token)==0:
            raise Exception(f"There is no API KEY in the env or database for model {self.model_name} - check ENV {params.get('token_env_key')}")
        headers = {
            "Content-Type": "application/json",
        }
        if params['scheme'] == 'openai':
            headers["Authorization"] = f"Bearer {token}"
            tools = self._elevate_functions_to_tools(functions)
        if params['scheme'] == 'anthropic':
            headers["x-api-key"] = token
            headers["anthropic-version"] = self.params.get('anthropic-version', "2023-06-01")
            tools = self._adapt_tools_for_anthropic(functions)
        if params['scheme'] == 'google':
            url = f"{url}?key={token}" if not is_streaming else f"{url.replace('generateContent','streamGenerateContent')}?alt=sse&key={token}"
        data = {
            "model": params['model'],
            "messages": [
                *[{'role': 'system', 'content': s} for s in [system_prompt] if s],
                {"role": "user", "content": question},
                #add in any data content into the stack for arbitrary models
                *data_content
            ],
            "tools": tools,
            'temperature': temperature
        }
        if is_streaming:
            data['stream'] = True
            data["stream_options"] = {"include_usage": True}
            
        if params['scheme'] == 'anthropic':
            data = {
                "model": params['model'],
                'temperature': temperature,
                "messages": [
                    {"role": "user", "content": question}, 
                    #because they use blocks https://docs.anthropic.com/en/docs/build-with-claude/tool-use#example-of-empty-tool-result
                    *[MessageStackFormatter.adapt_tool_response_for_anthropic(d) for d in data_content if d]
                ]
            }
            if tools:
                data['tools'] = tools
            if system_prompt:
                data['system'] = system_prompt
            if is_streaming:
                data['stream'] = True
                
            data["max_tokens"] = kwargs.get('max_tokens',ANTHROPIC_MAX_TOKENS_IN)
             
        if params['scheme'] == 'google':
            data_content = [MessageStackFormatter.adapt_tool_response_for_google(d) for d in data_content if d]
            optional_tool_config ={}#{ "tool_config": {   "function_calling_config": {"mode": "ANY"}  }  } #this seems to confuse the googs
            data = {
                "contents": [
                    {"role": "user", "parts": [{'text': question}]},
                    *data_content
                ],
                "tools": [{'function_declarations': tools}] if tools else None,
            }
            """gemini is stupid if you add a tool to use but it already has the answer
            "role": "user",  "parts": [{   "functionResponse": { <--- if the message is like this disable tools
            """
            if not data_content or 'functionResponse' not in data_content[-1]['parts'][0]:
                data.update(optional_tool_config)
            if system_prompt:
                data["system_instruction"] =  { "parts": { "text": system_prompt } }
                    
        logger.trace(f"request {data=}, {is_streaming=}")
   
        response =  requests.post(url, headers=headers, data=json.dumps(data), stream=is_streaming)
        
        if response.status_code not in [200,201]:
            logger.warning(f"failed to submit: {response.status_code=}  {response.content}")
        if response.status_code == 429:
            import time
            """TODO: should be a flagged thing"""
            time.sleep(61)
            logger.warning(f"RATE LIMITED - SLEEPING FOR 1 MINUTE")
            response =  requests.post(url, headers=headers, data=json.dumps(data),stream=is_streaming)   
        return response
    
    
    
    def parse_ai_response(self, partial: dict, usage: dict, ctx: CallingContext) -> AIResponse:
        """
        Normalize a partial LLM response (tool call or content) and usage dict into an AIResponse.
        
        This method creates an AIResponse object, then optionally audits it using the background worker.
        
        Args:
            partial: Partial response data (content or tool calls)
            usage: Token usage dictionary
            ctx: Calling context with session info
            
        Returns:
            AIResponse: The created response object
        """
        # Normalize the incoming payload to a plain dict
        if hasattr(partial, 'model_dump'):
            data = partial.model_dump()
        elif hasattr(partial, 'dict'):
            try:
                data = partial.dict()
            except Exception:
                data = {}
        elif isinstance(partial, dict):
            data = partial
        else:
            data = {}

        # Extract core fields
        content = data.get('content', '')
        role = data.get('role', 'assistant')
        tool_calls = data.get('tool_calls')
        tool_eval_data = data.get('tool_eval_data') or (data if tool_calls else None)
        verbatim = data.get('verbatim')
        function_stack = data.get('function_stack')

        # Token usage comes solely from the provided usage dict
        if usage and isinstance(usage, dict):
            tokens_in = usage.get('prompt_tokens', usage.get('input_tokens', 0))
            tokens_out = usage.get('completion_tokens', usage.get('output_tokens', 0))
        else:
            tokens_in = tokens_out = 0

        # Determine status based on presence of a tool call
        status = 'TOOL_CALL_RESPONSE' if tool_calls else 'COMPLETED'

        # Create the AIResponse object
        ai_response = AIResponse(
            id=str(uuid.uuid1()),
            model_name=self.model_name,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            session_id=ctx.session_id,
            role=role,
            content=content,
            status=status,
            tool_calls=tool_calls,
            tool_eval_data=tool_eval_data,
            verbatim=verbatim,
            function_stack=function_stack,
        )
        
        # Note: We're no longer auditing individual responses here
        # Auditing is now done comprehensively at the end of the stream using audit_response_for_user
        
        return ai_response
    
    def stream_with_proxy(self, messages, functions, context):
        """
        Stream LLM requests using the proxy architecture.
        
        This method handles the lower-level details of creating the appropriate
        request object and passing it to the proxy stream generator.
        
        Args:
            messages: MessageStack or list of message dictionaries
            functions: Function definitions to include in the request
            context: CallingContext with API credentials and settings
        
        Returns:
            Generator yielding (line, chunk) tuples
        """
        from percolate.services.llm.proxy.stream_generators import request_stream_from_model
        from percolate.services.llm.proxy.models import OpenAIRequest, AnthropicRequest, GoogleRequest
        
        message_data = messages.data if hasattr(messages, 'data') else messages
        
        R = OpenAIRequest
        if self._scheme == 'anthropic':
            R = AnthropicRequest 
        elif self._scheme == 'google':
            R = GoogleRequest 
         
        request = R(
            model=self.model_name,
            messages=message_data,
            stream=True,
            tools=functions
        )
        
        # Use proxy stream generator - source_scheme determined by model params
        return request_stream_from_model(
            request=request,
            context=context,
            target_scheme='openai',  
            relay_tool_use_events=False,  
            relay_usage_events=False  
        )
        
    def get_stream_iterator(self, content_generator, context:CallingContext, user_query:str=None, audit_on_flush:bool=False):
        """
        The stream iterator is a wrapper that helps with custom streaming logic, formatting and auditing
        
        Args:
            content_generator: Generator function that yields content
            context: CallingContext with user and session info
            audit_on_flush: If True, will audit the complete response when stream is done
        """
        # Wrap the streaming generator and collected AIResponses for auditing
        return LLMStreamIterator(
            content_generator,
            scheme=self._scheme,
            context=context,
            user_query=user_query,
            audit_on_flush=audit_on_flush
        )
        
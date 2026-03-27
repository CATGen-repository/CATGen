import pickle
import re
from loguru import logger
from openai import OpenAI
import openai
from transformers import AutoTokenizer


class LLM():
    def __init__(self, config):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                config['checkpoint_home']
            )
            self.api_key = config['key']
            self.base_url = config['api']
            self.temperature = config['temperature']
            self.top_p = config['top_p']
            self.max_tokens = config['max_tokens']
            self.model = config['model']
            self.stop = config['stop']
            self.response_header = config['response_header']
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except Exception:
            logger.error("Error loading configuration: llm.key or llm.api, please check the configuration file.")
            exit(-1)


    def _truncate_messages(self, messages, max_tokens, char_to_token_ratio=0.3):
        """
        根据token限制截断消息
        策略：从最旧的非系统消息开始移除或截断
        """
        bar = 500
        max_len = int(max_tokens * char_to_token_ratio)
        messages[-1]['content'] = messages[-1]['content'][:max_len - bar]
        return messages
    
    
    def _get_max_context_length(self, error_message):
        # 匹配类似 "maximum context length is 4097 tokens"
        match = re.search(r'maximum (?:context )?length is (\d+)', error_message)
        if match:
            return int(match.group(1)) - 10  # 留点余量给输出部分
        return None
    
    
    def get_response(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                stop=self.stop,
            )
        except openai.APIError as e:
            try:
                # 判断一下是不是prompt超长了
                error_msg = str(e).lower()
                
                if "maximum" in error_msg and ("context" in error_msg or "input length" in error_msg):
                    print("输入长度超出限制，尝试截断...")

                    max_tokens = self._get_max_context_length(error_msg)
                    if not max_tokens:
                        max_tokens = 16384

                    print(f"将 prompt 截断为 {max_tokens} 个 token")
                    messages = self._truncate_messages(messages, max_tokens)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=False,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                    stop=self.stop,
                )
            except openai.APIError as e:
                logger.error(str(e))
                return ""
        return response.choices[0].message.content


    def get_response_with_prefix(self, messages, prefix='```java\nassertEquals('):
        if 'Phind' in self.model:
        # For Phind model.
            system_prompt = '### System Prompt\n'
            user_prompt = '### User Message\n'
            for one_message in messages:
                if one_message['role'] == 'system':
                    system_prompt += one_message['content']+'\n\n'
                elif one_message['role'] =='user':
                    user_prompt += one_message['content']+'\n\n'

            prompt = system_prompt + user_prompt
            prompt += '### Assistant\n'+"To test the given method, we will need to cover various scenarios. Here is the test class implementation:\n"+prefix
        
        else:
        # For other models.
            new_message = pickle.loads(pickle.dumps(messages))
            prompt = self.tokenizer.apply_chat_template(new_message, tokenize=False)
            prompt +=  self.response_header + "To test the given method, we will need to cover various scenarios. Here is the test class implementation:\n"+prefix
            tmp_message = [
                {'role':'user','content':'USER'},
                {'role':'assistant','content':'ASSISTANT'},
            ]
            
        openai.api_key = self.api_key
        openai.base_url = self.base_url
        response = openai.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            stop = self.stop
        )
        return prefix +  response.choices[0].text
    
    
    def get_tokens_cnt(self, messages, ans_prompt=''):
        prompt = ''
        for message in messages:
            prompt += message["role"] + ':' + message["content"] + "\n"
        prompt += ans_prompt
        return len(self.tokenizer.tokenize(prompt))




if __name__ == '__main__':
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.configuration import configs
    allm = LLM(configs['Qwen2.5-Coder-32B-Instruct'])
    message = [
        {"role": "user", "content":  "Give me a quick sort code."},
    ]
    # response = allm.get_response(message)
    print(allm.get_response(message))
    a = 1

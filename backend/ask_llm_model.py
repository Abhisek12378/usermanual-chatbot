from config_loader import AppConfig
from langchain_openai import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import langchain
from langchain.chat_models import ChatOpenAI
import json
config=AppConfig()
class LanguageProcessing:
    def __init__(self, openai_api_key=config.openai_api_key, temperature=config.open_ai_temperature):
        self.llm = ChatOpenAI(model_name='gpt-4',openai_api_key=openai_api_key,temperature=temperature,verbose=True)
        ##self.llm = OpenAI(openai_api_key=openai_api_key,temperature=temperature, model_name="gpt-4",verbose=True)
        self.temperature = float(temperature)
        self.openai_api_key=openai_api_key

    def predict_task_type(self, filetype, query):
        generic_template = '''
            Imagine you are a chatbot. A user has uploaded a {filetype} file and asked a question: "{task_desc}". Your task is to determine the type of task the user wants to perform, based on the question provided. There are only three possible tasks you can choose from: Question Answering, Summarization, and Translation.

            Based on the content of the question, select the most appropriate task:
            - If the question explicitly asks for a concise summary of the content, respond with: "Summarization".
            - If the question explicitly asks for the content to be translated from one language to another, respond with: "Translation".
            - For all other types of queries, default to: "Question Answering".

            Given the task description "{task_desc}", what is the most appropriate task type? Please respond in JSON format with the "task_type" key.
        '''

        # Example usage:
        # Assume this function is called within a context where `filetype` and `task_desc` are defined.
        formatted_prompt = generic_template.format(filetype="PDF", task_desc="How can I summarize this document?")

        prompt = PromptTemplate(input_variables=['filetype', 'task_desc'], template=generic_template)
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        result = llm_chain.run({'filetype': filetype, 'task_desc': query})
        print("Raw model output:", result)

        try:
            # Assuming the result is a JSON string directly
            parsed_json = json.loads(result.strip())
            task_type = parsed_json['task_type']
        except json.JSONDecodeError:
            task_type = "Error: Failed to decode JSON from model output."
        except KeyError:
            task_type = "Error: The required key 'task_type' is not present."

        return task_type

    def do_embedding(self, info_text):
        openai_embedding=OpenAIEmbeddings()
        vectordb = FAISS.from_documents(documents=info_text, embedding=openai_embedding)
        return vectordb

    def summarize_text(self, info_chunk, query_value):
        llm = OpenAI(openai_api_key=self.openai_api_key, temperature=self.temperature, verbose=True)
        chunks_prompt = ''' 
        {query}
        Speech:`{text}'
        Summary:
        '''
        map_prompt_template = PromptTemplate(input_variables=['text'], template=chunks_prompt.format(query=query_value, text="{text}"))
        summary_chain = load_summarize_chain(llm=llm, chain_type='map_reduce', map_prompt=map_prompt_template, verbose=False)
        output = summary_chain.run(info_chunk)
        return output

    def question_answering(self, vector_db, query_value):
        retriever = vector_db.as_retriever(score_threshold=0.7)
        langchain.debug = True
        prompt_template = """
        Use the provided context from a user manual to generate a response to the question. When answering, follow these guidelines:
        - If the user manual content that answers the question is formatted in points, maintain this format in the response. Reflect the original wording as closely as possible.
        - If the content directly addresses the question with specific statements, use exact quotes.
        - For general inquiries where summarization is needed and no point format is given, provide the answer in concise prose or point form based on the complexity of the information.

        If no information in the user manual directly answers the question, respond with "Content not available in the user manual for this query."

        Be mindful of the token limits and aim to complete your response within these limits. If approaching the token limit, finish the last sentence fully rather than starting a new one that cannot be completed.

        Assess the complexity and depth of the question to determine the appropriate length and format of the answer, aiming for precision and relevance.

        --- User Manual Context Begins ---
        {context}
        --- User Manual Context Ends ---

        --- User Inquiry ---
        {question}
        --- End of Inquiry ---
        """
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=retriever,
                                            input_key="query", return_source_documents=True,
                                            chain_type_kwargs={"prompt": PROMPT})
        json_result = chain(query_value)
        result = json_result['result']

        return result
    def language_translation(self,info_chunk,query_value):
        llm = OpenAI(openai_api_key=self.openai_api_key, temperature=self.temperature, verbose=True)
        query_chain_template = '''
        We need to perform a language translation task. For the query provided below, determine the target language to which we have to translate the content.
        {query_text}
        The output should be the name of the target language, represented as a single word (e.g., "English").
        '''
        query_chain_template_name = PromptTemplate(template=query_chain_template, input_variables=["query_text"])
        query_chain = LLMChain(llm=llm, prompt=query_chain_template_name)
        target_language_result = query_chain.run(query_value)
        translation_prompt_template = '''
        Translate the following text from English to {target_language} and don't add English version of it in output
        {text}
        '''
        translation_chain_template_name = PromptTemplate(template=translation_prompt_template,
                                                         input_variables=["target_language", "text"])
        translation_chain = LLMChain(llm=self.llm, prompt=translation_chain_template_name)
        final_result=""
        for content in info_chunk:
            translation_result = translation_chain.run({"target_language": target_language_result, "text": content})
            final_result=final_result+"\n"+translation_result
        return final_result





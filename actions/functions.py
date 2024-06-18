from pymongo import MongoClient


def get_db_connection():
    """Connect to Mongo Database"""

    # mongo_uri = "mongodb://%s:%s@%s:%s/%s?authSource=%s" % (
    #     quote_plus(os.environ["DB__USER"]),
    #     quote_plus(os.environ["DB__PASS"]),
    #     quote_plus(os.environ["DB__HOST"]),
    #     quote_plus(os.environ["DB__PORT"]),
    #     quote_plus(os.environ["DB_"]),
    #     quote_plus(os.environ["AUTH_DB_"]))
    # client = MongoClient(mongo_uri)
    # db = client[quote_plus(os.environ["DB_"])]
    client = MongoClient('localhost', 27017)
    db = client["Rasa_chatbots"]
    return db


db = get_db_connection()
__keyphrases_list__ = db.faq.distinct("keyphrase_lower")


def fetch_faq_question_answer(question: str, keyphrase: str, module=None) -> list:
    """

    :param keyphrase:
    :return:
    """
    print("@", question, "@", module)
    if question:
        filter_obj = {"question_lower": question}
        if module != "search across":
            filter_obj["module name"] = module
        res = list(db.faq.find(filter_obj))
    else:
        res = list(db.faq.find({"keyphrase_lower": keyphrase.lower()}))

    return res


def extract_keyphrase(user_message: str) -> list:
    """

    :param user_message:
    :return:
    """
    extracted_keyphrase_list = []
    # Loop Keyphrase list
    for keyphrase in __keyphrases_list__:
        if keyphrase in user_message.lower():
            extracted_keyphrase_list.append(keyphrase)

    return extracted_keyphrase_list


def extract_metadata_from_tracker(tracker):
    events = tracker.current_state()['events']
    user_events = []
    for e in events:
        if e['event'] == 'user':
            user_events.append(e)
    return user_events[-1]['metadata']


def get_questions(module: str) -> list:
    """

    :param module:
    :return: Questions list
    """
    questions_list = []
    res = db.faq.distinct("question", {"module name": module})

    for question in res:
        questions_list.append(dict(title=question, payload=question))
    questions_list.append(dict(title="My Question Not here", payload="My Question Not here"))

    return questions_list


def add_user_feedback_logs(tracker):
    """

    :param tracker:
    :return:
    """
    user_id = tracker.get_slot('user_id')
    module_selection = tracker.get_slot('module')
    question = tracker.get_slot('question')
    bot_answer = tracker.get_slot('answer')
    support_type = tracker.get_slot('support_type')
    response_feedback = tracker.get_slot('reponse_feedback')
    feedback_rating = tracker.get_slot('feed_back_rating')

    user_feedback = dict(user_id=user_id,
                         module_selection=module_selection,
                         question=question,
                         bot_answer=bot_answer,
                         support_type=support_type,
                         response_feedback=response_feedback,
                         feedback_rating=feedback_rating)

    db.user_feedback_logs.insert_one(user_feedback)

    return True



import os
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.base import Document


def set_openai_api_key(api_key):
    os.environ["OPENAI_API_KEY"] = api_key


def extract_text_from_pdf(file_paths):
    raw_text = ''
    for file_path in file_paths:
        doc_reader = PdfReader(file_path)
        for i, page in enumerate(doc_reader.pages):
            text = page.extract_text()
            if text:
                raw_text += text
    return raw_text


def split_text_into_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_text(text)
    return texts



def initialize_embeddings():
    embeddings = OpenAIEmbeddings()
    return embeddings


def create_prompt_template(template, input_variables):
    return PromptTemplate(input_variables=input_variables, template=template)


def create_conversation_buffer_memory(memory_key, input_key):
    return ConversationBufferMemory(memory_key=memory_key, input_key=input_key)


def load_question_answering_chain(llm, chain_type, memory, prompt):
    return load_qa_chain(llm, chain_type=chain_type, memory=memory, prompt=prompt)


def create_retriever(texts, embeddings):
    docsearch = FAISS.from_texts(texts, embeddings)
    return docsearch


def get_summary(llm, text):
    document = Document(page_content=text)
    documents = [document]
    chain = load_summarize_chain(llm=llm, chain_type="stuff")
    summary = chain.run(documents)
    return summary






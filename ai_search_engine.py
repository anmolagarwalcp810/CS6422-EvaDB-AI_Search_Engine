import evadb
import os
import pandas as pd
from collections import OrderedDict
import warnings
import time
from colorama import Fore, Back, Style

"""
        AI Search Engine
        Author: Anmol Agarwal (aagarwal622)
        Date: 10.15.2023
"""

warnings.filterwarnings("ignore")
# This cursor will be used through the whole code to run AI queries
print("Connecting to evaDB")
cursor = evadb.connect().cursor()

# Few global variables and constants
SIMILARITY_THRESHOLD = 1.0
PARAGRAPHS_LIMIT = 10
DEFAULT_DOCS_PATH = "docs"
DEFAULT_SENTENCE_FEATURE_EXTRACTOR_PATH = "./functions/sentence_feature_extractor.py"
user_defined_limit = PARAGRAPHS_LIMIT
user_defined_summarize = False
polling_interval = 10


# Break txt document into paragraphs (similar to how we do for pdf) and insert into my Documents.
def insert_text_file(path: str) -> None:
    data = ""
    try:
        file = open(path, "r")
        data = file.read().split("\n")
    except:
        print("Unable to open file {}".format(path))
        return

    # insertion query
    insert_query = """
        INSERT INTO MyDocuments(name, page, paragraph, data) VALUES
        {};
    """

    count = 1
    for i in range(len(data)):
        data[i] = data[i].strip()
        if data[i].isspace() or len(data[i]) == 0:
            continue
        values = "('{}', 1, {}, '{}')".format(path, count, data[i])
        # print("New insert query: {}".format(insert_query.format(values)))
        cursor.query(insert_query.format(values)).df()
        count += 1


# this function will take care of merging PDFs into overall MyDocuments table containing both text and pdf data
def merge_pdfs():
    mypdfs_df = cursor.query("SELECT * FROM MyPDFs").df()

    # insert query
    insert_query = """
        INSERT INTO MyDocuments(name, page, paragraph, data) VALUES
        ('{}', {}, {}, '{}');
    """

    # insert all data from MyPDFs into MyDocuments
    for index, row in mypdfs_df.iterrows():
        cursor.query(insert_query.format(row['mypdfs.name'], row['mypdfs.page'], row['mypdfs.paragraph'],
                                         row['mypdfs.data'])).df()


def read_and_store_documents(path: str = DEFAULT_DOCS_PATH) -> None:
    drop_table_query = "DROP TABLE IF EXISTS MyDocuments"
    drop_pdfs_query = "DROP TABLE IF EXISTS MyPDFs"
    create_table_query = """
            CREATE TABLE MyDocuments (
                name TEXT(0),
                page INTEGER,
                paragraph INTEGER,
                data TEXT(0)
            );
        """

    # drop table if exists
    cursor.query(drop_table_query).df()
    cursor.query(drop_pdfs_query).df()

    # create table query
    cursor.query(create_table_query).df()

    files = os.listdir(path)
    for i in range(len(files)):
        files[i] = f"{path}/{files[i]}"

    add_documents(files)

    # drop pdfs table now
    cursor.query(drop_pdfs_query).df()

    print("MyDocuments table initialized!")


# Create database MyDocuments from files stored in pdfs/
def add_documents(list_of_documents: list[str]) -> None:
    load_pdfs_query = "LOAD PDF '{}' INTO MyPDFs"
    count_pdfs = 0
    for file in list_of_documents:
        if file.endswith(".pdf"):
            # add each pdf file while also checking extension
            cursor.query(load_pdfs_query.format(file)).df()
            count_pdfs += 1
        elif file.endswith(".txt"):
            # add each text file by calling insert_text_file
            insert_text_file(f"{file}")

    if count_pdfs > 0:
        merge_pdfs()


# Create sentence feature extractor function
def create_sentence_feature_extractor(path: str = DEFAULT_SENTENCE_FEATURE_EXTRACTOR_PATH) -> None:
    drop_function_query = "DROP FUNCTION IF EXISTS SentenceFeatureExtractor"
    create_function_query = "CREATE FUNCTION SentenceFeatureExtractor IMPL '{}'".format(path)
    # drop SentenceFeatureExtractor function if exists
    cursor.query(drop_function_query).df()
    # now create SentenceFeatureExtractor Function
    cursor.query(create_function_query).df()

    print("Sentence Feature Extractor created")


# Create vector index for embedding entries in MyDocuments database, so that we can run fast queries later on.
def create_embeddings_vector_index() -> None:
    create_vector_index_query = """
        CREATE INDEX feature_index
        ON MyDocuments (SentenceFeatureExtractor(data))
        USING QDRANT
    """
    cursor.query(create_vector_index_query).df()

    print("Vector Index for SentenceFeatureExtractor created")


# Now we get results from the MyDocuments table on incoming query.
def get_query_results(search_query: str, limit: int = PARAGRAPHS_LIMIT) -> OrderedDict:
    """
    We implement the following logic:
        1. Get all paragraphs sorted in decreasing order of similarity and exclude results with similarity less than threshold.
        2. Group the paragraphs by documents and order the documents in decreasing order of similarity.
        3. Document similarity is simply the average similarity of relevant paragraphs for each document.
        4. Finally, we output the paragraphs grouped by documents as mentioned above to the user.
    Returns document names and their corresponding paragraphs ordered by document similarity and then by paragraph similarity.
    """
    result_query = f"""
        SELECT scored_paragraphs.name, scored_paragraphs.paragraph, scored_paragraphs.data, scored_paragraphs.distance
        FROM (
            SELECT name, paragraph, data, Similarity(SentenceFeatureExtractor('{search_query}'), SentenceFeatureExtractor(data)) 
            FROM MyDocuments
        ) AS scored_paragraphs
        WHERE scored_paragraphs.distance >= {SIMILARITY_THRESHOLD}
        ORDER BY scored_paragraphs.distance DESC
        LIMIT {limit}
    """
    scored_paragraphs_df = cursor.query(result_query).df()
    scored_documents_df = scored_paragraphs_df.groupby('scored_paragraphs.name')['scored_paragraphs.distance'].mean().to_frame()
    scored_documents_df = scored_documents_df.sort_values(by='scored_paragraphs.distance', ascending=False)

    documents_dictionary = OrderedDict()

    for index, row in scored_documents_df.iterrows():
        documents_dictionary[index] = []

    for index, row in scored_paragraphs_df.iterrows():
        document_name = row["scored_paragraphs.name"]
        paragraph_id = row["scored_paragraphs.paragraph"]
        paragraph_data = row["scored_paragraphs.data"]
        similarity_score = row["scored_paragraphs.distance"]
        documents_dictionary[document_name].append((paragraph_id, paragraph_data, similarity_score))

    # print(documents_dictionary)

    return documents_dictionary


# Now we output the results of the query
def return_results(documents_dictionary: OrderedDict) -> str:
    output = []
    for key, value in documents_dictionary.items():
        output.append(f"{Fore.LIGHTYELLOW_EX}{key}")
        count = 0
        for i in value:
            output.append(f"{Style.RESET_ALL}\033[1m\033[2m\033[3m\033[4mRelevant Text {count}{Style.RESET_ALL}")
            output.append(f"{Fore.GREEN}{i[1]}")
            count += 1
        output.append(f"{Fore.LIGHTMAGENTA_EX}{'@'*100}")

    return '\n'.join(output)


# Summarize with LLM (Facebook bart cnn) if needed
def summarize_with_LLM(documents_dictionary: OrderedDict) -> str:
    # First develop prompt
    prompt = []
    for key, value in documents_dictionary.items():
        for i in value:
            prompt.append(i[1])
    prompt = '\n'.join(prompt)
    # Since we want to apply text summarizer, we will need to create a table containing the above prompt
    # and run the text summarizer on that

    # table creation query (TEXT(0) didn't really limit the length of data stored)
    create_table_query = """
        CREATE TABLE PromptData
        (id INTEGER,
        data TEXT(0));
    """

    # prompt insertion query
    insert_prompt_query = f"""
        INSERT INTO PromptData (id, data) VALUES
        (1, '{prompt}');
    """

    # after this, we will call table function to summarize the prompt using bart LLM (can try with others too)
    summarization_query = "SELECT TextSummarizer(data) FROM PromptData"

    # drop table query
    drop_table_query = """
        DROP TABLE IF EXISTS PromptData
    """

    # run the queries
    cursor.query(create_table_query).df()
    cursor.query(insert_prompt_query).df()
    df = cursor.query(summarization_query).df()
    cursor.query(drop_table_query).df()

    return df.iloc[0, 0]


# create summarization function
def create_text_summarizer():
    create_summarizer_query = """
        CREATE FUNCTION IF NOT EXISTS TextSummarizer
        TYPE HuggingFace
        TASK 'summarization'
        MODEL 'facebook/bart-large-cnn'
    """
    cursor.query(create_summarizer_query).df()
    print("Text summarizer created")


# initialize all tables and functions
def initialize():
    read_and_store_documents()
    create_sentence_feature_extractor()
    create_text_summarizer()
    create_embeddings_vector_index()


def process_one_query() -> bool:
    global user_defined_summarize
    global user_defined_limit
    query = input("Query: ")
    if query == "exit":
        print(f"{Fore.RED}{Back.WHITE}Exiting...{Style.RESET_ALL}")
        return True
    elif query == "SUMMARIZE":
        print(f"{Fore.GREEN}{Back.BLACK}Summarization enabled!{Style.RESET_ALL}")
        user_defined_summarize = True
    elif query == "DISABLE SUMMARIZE":
        print(f"{Fore.GREEN}{Back.BLACK}Summarization disabled!{Style.RESET_ALL}")
        user_defined_summarize = False
    elif query.startswith("LIMIT"):
        l = query.split()
        if len(l) == 2 and l[1].isdecimal():
            user_defined_limit = int(l[1])
            print(f"{Fore.GREEN}{Back.BLACK}Limit set to {user_defined_limit}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{Back.WHITE}Invalid input for LIMIT. Syntax: LIMIT INTEGER{Style.RESET_ALL}")
    elif query == "SHOW":
        print(f"{Fore.GREEN}{Back.BLACK}")
        print(cursor.query("SELECT * FROM MyDocuments").df())
        print(f"{Style.RESET_ALL}")
    else:
        documents_dictionary = get_query_results(query, user_defined_limit)
        if user_defined_summarize:
            print(f"{Back.GREEN}{Fore.BLACK}Summary:{Back.RESET}{Fore.CYAN}\n{summarize_with_LLM(documents_dictionary)}{Style.RESET_ALL}")
        print(f"{return_results(documents_dictionary)}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{Back.YELLOW}{'#' * 200}{Style.RESET_ALL}")
    return False


# This function repeatedly checks docs folder every 10 seconds and updates database
# if docs folder has changed.
def poll_and_update_table(path: str = DEFAULT_DOCS_PATH):
    drop_pdfs_query = "DROP TABLE IF EXISTS MyPDFs"
    delete_doc_query = "DELETE FROM MyDocuments WHERE name = '{}'"

    # drop PDFs table if needed
    cursor.query(drop_pdfs_query).df()

    select_docs_query = "SELECT name FROM MyDocuments"

    docs_df = cursor.query(select_docs_query).df()
    stored_docs = set(docs_df['mydocuments.name'].to_list())

    docs_in_directory = set()
    directory_list = os.listdir(path)

    for doc in directory_list:
        docs_in_directory.add(f"{path}/{doc}")

    docs_to_remove = stored_docs.difference(docs_in_directory)
    docs_to_add = docs_in_directory.difference(stored_docs)

    for doc in docs_to_remove:
        cursor.query(delete_doc_query.format(doc)).df()

    add_documents(list(docs_to_add))

    # drop pdfs
    cursor.query(drop_pdfs_query).df()

    if len(docs_to_add) > 0 or len(docs_to_remove) > 0:
        print(f"{Back.BLACK}{Fore.MAGENTA}Updated the database!\nAdded {', '.join(list(docs_to_add))}\nRemoved {', '.join(list(docs_to_remove))}{Style.RESET_ALL}")


# Complete end to end flow of query from user
def process_query():
    initialize()
    print(f"{Fore.BLACK}{Back.WHITE}Initialized all tables and functions{Style.RESET_ALL}")
    curr_time = time.time()
    while True:
        if time.time() - curr_time >= polling_interval:
            poll_and_update_table()
            curr_time = time.time()
        should_break = process_one_query()
        if should_break: break


# Main program running process_query to get queries from users.
if __name__ == "__main__":
    print("Engine started")
    process_query()

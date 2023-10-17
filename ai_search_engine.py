import evadb
import os
import pandas as pd
from collections import OrderedDict
import warnings

"""
        AI Search Engine
        Author: Anmol Agarwal (aagarwal622)
        Date: 10.15.2023
"""

warnings.filterwarnings("ignore")
# This cursor will be used through the whole code to run AI queries
print("Connecting to evaDB")
cursor = evadb.connect().cursor()

# Few constants
SIMILARITY_THRESHOLD = 0.7
PARAGRAPHS_LIMIT = 10
DEFAULT_PDFS_PATH = "./pdfs"
DEFAULT_SENTENCE_FEATURE_EXTRACTOR_PATH = "./functions/sentence_feature_extractor.py"


# Break txt document into paragraphs (similar to how we do for pdf) and insert into my Documents.
def insert_text_file(name: str, path: str) -> None:
    try:
        file = open(path, "r")
    except:
        print("Unable to open file {}".format(path))

    data = file.read().split("\n")

    # insertion query
    insert_query = """
        INSERT INTO MyDocument(name, page, paragraph, data) VALUES
        {}
    """

    for i in range(len(data)):
        if(data[i].isspace()):
            continue
        values = "('{}', 1, {}, '{}');".format(name, i+1, data[i])
        cursor.query(insert_query.format(values)).df()


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
        cursor.query(insert_query.format(row['mypdfs.name'], row['mypdfs.page'], row['mypdfs.paragraph'], row['mypdfs.data'])).df()


# Create database MyDocuments from files stored in pdfs/
def create_my_documents(path: str = DEFAULT_PDFS_PATH) -> None:
    drop_table_query = "DROP TABLE IF EXISTS MyDocuments"
    drop_pdfs_query = "DROP TABLE IF EXISTS MyPDFs"
    load_pdfs_query = "LOAD PDF '{}/{}' INTO MyPDFs"
    # drop table if exists
    cursor.query(drop_table_query).df()
    files = os.listdir(path)
    for file in files:
        if file.endswith(".pdf"):
            # add each pdf file while also checking extension
            cursor.query(load_pdfs_query.format(path, file)).df()
        elif file.endswith(".txt"):
            # add each text file by calling insert_text_file
            insert_text_file(f"{path}/{file}")
    
    merge_pdfs()

    print("MyDocuments table initialized")


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
        documents_dictionary[index]=[]

    for index, row in scored_paragraphs_df.iterrows():
        document_name = row["scored_paragraphs.name"]
        paragraph_id = row["scored_paragraphs.paragraph"]
        paragraph_data = row["scored_paragraphs.data"]
        similarity_score = row["scored_paragraphs.distance"]
        documents_dictionary[document_name].append((paragraph_id, paragraph_data, similarity_score))

    return documents_dictionary


# Now we output the results of the query
def return_results(documents_dictionary: OrderedDict) -> str:
    output = []
    for key, value in documents_dictionary.items():
        output.append(key)
        count = 0
        for i in value:
            output.append("Relevant Text {}".format(count))
            output.append(i[1])
            count+=1
        output.append("-----------------------------------------------")

    return '\n'.join(output)


# Summarize with LLM if needed
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
    create_my_documents()
    create_sentence_feature_extractor()
    create_text_summarizer()
    create_embeddings_vector_index()


# Complete end to end flow of query from user
def process_query():
    limit = PARAGRAPHS_LIMIT
    summarize = False
    initialize()
    print("Initialized all tables and functions")
    while True:
        query = input("Query: ")
        if query == "exit":
            print("Exiting...")
            break
        elif query == "SUMMARIZE":
            print("Summarization enabled!")
            summarize = True
            continue
        elif query == "NOT SUMMARIZE":
            print("Summarization disabled!")
            summarize = False
            continue
        elif query.startswith("LIMIT"):
            l = query.split()
            if len(l) == 2 and l[1].isdecimal():
                limit = int(l[1])
                print("Limit set to {}".format(limit))
            else:
                print("Invalid input for LIMIT. Syntax: LIMIT INTEGER")
            continue

        documents_dictionary = get_query_results(query, limit)
        if summarize:
            print(summarize_with_LLM(documents_dictionary))
        print(return_results(documents_dictionary))
        print("_"*100)


# Main program running process_query to get queries from users.
if __name__ == "__main__":
    print("Engine started")
    process_query()

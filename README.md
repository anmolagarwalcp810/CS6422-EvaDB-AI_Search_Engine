# Current Plan (Will Update readme with full report later on)
## Salient Features
1. Reads PDFs and stores them by paragraphs in db. [Done]
2. Uses Vector Indexes to gather sentence embeddings. [Done]
3. Takes in query and gets top 10 paragraphs with highest similarity score. [Done]
   1. User can change limit for number of relevant paragraphs.
   2. And it then outputs the documents in order of highest similarity (calculated as average of similarity score for all paragraphs). 
   3. Use query results to consolidate the documents. 

Above was the most basic implementation as needed. Now we talk about additional features which we can add:
1. Use LLM to summarize the relevant paragraphs for the user, so that they can also get summary for their query. [Done]
2. Also support for txt documents. Straightforward!! Just add their data into MyDocuments. [Done]
3. Adding another feature (use threads) to repeatedly poll the directory containing documents and update database if directory has changed (like new documents added, removed). (For Modified Case, will think about in part 2.) [Current] 
4. Check correctness of algorithm. [Done]

## Possible Extensions Part 2 of EvaDB Project
1. Will think if we can add more features like document clustering and more advanced queries like “Tell me about spring in context of computer science”, this will only get results from documents clustered under computer science and give info about spring framework for Java. Or “Tell me about spring in context of nature”, this will get results documents clustered under nature and give info about the spring season.
2. Use ChatGPT or GPT4All to also summarize the documents in 1 line for the user and store in MyPDFs. If user asks for summary, just output the summary of all documents. Perhaps can create an abstract function for that.
3. Use different Sentence Feature Extractor through different model (probably OpenAI) and qualitatively compare the output.

All of these above extensions can be taken up in Project 2.

## Status
Most of the above implemented. 

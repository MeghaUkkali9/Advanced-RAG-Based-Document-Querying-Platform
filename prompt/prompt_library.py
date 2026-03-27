from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant trained to analyse and summarize documents.
Return ONLY valid JSON matching schema below.
{format_instructions}

Analyse this Document:
{document_text}
""")

document_comparison_prompt = ChatPromptTemplate.from_template("""
Compare two documents (combined below).

- Identify differences page-wise
- Separate into:
  - added (present in actual, not in reference)
  - deleted (present in reference, not in actual)
- If no change → "NO CHANGE"

Return ONLY JSON:
{format_instructions}

Documents:
{combined_document}
""")

contextualize_question_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Given a conversation history and the most recent user query, rewrite the query as a standalone question "
        "that makes sense without relying on the previous context. Do not provide an answer—only reformulate the "
        "question if necessary; otherwise, return it unchanged."
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

context_qa_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an assistant designed to answer questions using the provided context. Rely only on the retrieved "
        "information to form your response. If the answer is not found in the context, respond with 'I don't know.' "
        "Keep your answer concise and no longer than three sentences.\n\n{context}"
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

PROMPT_REGISTRY={
    "document_analysis": prompt,
    "document_comparison": document_comparison_prompt,
    "contextualize_query": contextualize_question_prompt,
    "context_query_answering": context_qa_prompt
}
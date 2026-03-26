from langchain.prompts import ChatPromptTemplate

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

PROMPT_REGISTRY={
    "document_analysis": prompt,
    "document_comparison": document_comparison_prompt
}
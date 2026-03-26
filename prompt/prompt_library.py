from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant trained to analyse and summarize documents.
Return ONLY valid JSON matching schema below.
{format_instructions}

Analyse this Document:
{document_text}
""")

document_comparison_prompt = ChatPromptTemplate.from_template("""
You are a document comparison assistant.

Compare the two documents (combined below).

- Identify differences page-wise
- Mention only meaningful changes
- If no difference → "NO CHANGE"

Return ONLY JSON:
{format_instruction}

Documents:
{combined_docs}
""")

PROMPT_REGISTRY={
    "document_analysis": prompt,
    "document_comparison": document_comparison_prompt
}
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant trained to analyse and summarize documents.
Return ONLY valid JSON matching schema below.
{format_instructions}

Analyse this Document:
{document_text}
""")

document_comparison_prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant trained to compare two documents and summarize the differences.
Return ONLY valid JSON matching schema below.
{format_instructions}

Compare these Documents:
Document 1: {document_1_text}
Document 2: {document_2_text}
""")

PROMPT_REGISTRY={
    "document_analysis": prompt,
    "document_comparison": document_comparison_prompt
}
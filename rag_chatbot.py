import pandas as pd
import faiss
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer


class RAGChatbot:

    def __init__(self, api_key: str):

        genai.configure(api_key=api_key)

        self.ai_model = genai.GenerativeModel("gemini-2.5-flash")

        self.embed_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.index = None
        self.context_strings = []

    def build_vector_store(self, df: pd.DataFrame):

        self.context_strings = []

        for _, row in df.iterrows():

            self.context_strings.append(
                f"""
Date: {row['Date'].strftime('%Y-%m-%d')}
Description: {row['Description']}
Amount: {row['Amount']}
Category: {row['Category']}
"""
            )

        embeddings = self.embed_model.encode(
            self.context_strings,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(
            embeddings.astype("float32")
        )

    def answer_query(self, query: str):

        if self.index is None:
            return "Please upload a transaction file first."

        query_embedding = self.embed_model.encode(
            [query],
            convert_to_numpy=True
        )

        k = min(5, len(self.context_strings))

        _, indices = self.index.search(
            query_embedding.astype("float32"),
            k
        )

        context = "\n\n".join(
            self.context_strings[i]
            for i in indices[0]
            if i != -1
        )

        prompt = f"""
You are an AI Financial Assistant.

Answer ONLY using the transaction data below.

If the answer is not available in the data,
reply:

"I couldn't find that information in the uploaded statement."

Transactions:

{context}

Question:

{query}
"""

        try:

            response = self.ai_model.generate_content(prompt)

            return response.text

        except Exception as e:

            return f"Error: {str(e)}"
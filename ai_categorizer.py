import json
import google.generativeai as genai
import pandas as pd
from typing import Dict


class AICategorizer:

    def __init__(self, api_key: str):

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        self.categories = [
            "Travel",
            "Food & Drinks",
            "Rent",
            "Shopping",
            "Health",
            "Investment",
            "Bills",
            "Entertainment",
            "Education",
            "Salary",
            "Transfer",
            "Other"
        ]

    def batch_categorize(
        self,
        df: pd.DataFrame,
        batch_size: int = 20
    ) -> pd.DataFrame:

        df = df.copy()

        categories = []
        confidence = []

        system_prompt = f"""
You are a finance expert.

Categorize every transaction into ONE category only.

Categories:

{self.categories}

Return ONLY valid JSON.

Example:

{{
    "results":[
        {{
            "id":0,
            "category":"Food & Drinks",
            "confidence":0.95
        }}
    ]
}}
"""

        for start in range(0, len(df), batch_size):

            batch = df.iloc[start:start + batch_size]

            payload = []

            for idx, row in batch.iterrows():

                payload.append({
                    "id": int(idx),
                    "description": str(row["Description"]),
                    "amount": float(row["Amount"])
                })

            prompt = system_prompt + "\n\nTransactions:\n" + json.dumps(payload)

            try:

                response = self.model.generate_content(prompt)

                text = response.text.strip()

                text = (
                    text.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

                result = json.loads(text)

                lookup = {
                    item["id"]: item
                    for item in result.get("results", [])
                }

                for idx in batch.index:

                    if idx in lookup:

                        categories.append(
                            lookup[idx].get("category", "Other")
                        )

                        confidence.append(
                            float(
                                lookup[idx].get("confidence", 0.5)
                            )
                        )

                    else:

                        categories.append("Other")
                        confidence.append(0.0)

            except Exception as e:

                print("Categorization Error:", e)

                for _ in range(len(batch)):
                    categories.append("Other")
                    confidence.append(0.0)

        df["Category"] = categories
        df["Confidence"] = confidence

        return df

    def generate_insights(
        self,
        df: pd.DataFrame
    ) -> Dict:

        summary = (
            df.groupby("Category")["Amount"]
            .sum()
            .round(2)
            .to_dict()
        )

        prompt = f"""
You are a financial advisor.

Analyze this expense summary.

{json.dumps(summary, indent=2)}

Return ONLY JSON.

{{
"spending_habits_summary":"",
"savings_recommendations":["","",""],
"financial_health_score":75
}}
"""

        try:

            response = self.model.generate_content(prompt)

            text = (
                response.text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(text)

        except Exception as e:

            print("Insight Error:", e)

            return {
                "spending_habits_summary":
                    "Unable to generate AI insights.",

                "savings_recommendations":[
                    "Review high-value expenses.",
                    "Track monthly spending.",
                    "Create a monthly savings budget."
                ],

                "financial_health_score":50
            }
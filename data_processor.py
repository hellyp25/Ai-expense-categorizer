import pandas as pd
import pdfplumber
import re


class DataProcessor:

    @staticmethod
    def load_file(uploaded_file) -> pd.DataFrame:
        """Load CSV, Excel, ODS or PDF."""

        file_name = uploaded_file.name.lower()

        if file_name.endswith(".csv"):
            return pd.read_csv(uploaded_file)

        elif file_name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)

        elif file_name.endswith(".ods"):
            return pd.read_excel(uploaded_file, engine="odf")

        elif file_name.endswith(".pdf"):
            return DataProcessor._parse_pdf(uploaded_file)

        else:
            raise ValueError("Unsupported file format.")

    @staticmethod
    def _parse_pdf(uploaded_file) -> pd.DataFrame:

        text_lines = []

        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_lines.extend(text.split("\n"))

        parsed = []

        for line in text_lines:

            date = re.search(
                r"\d{2}[/-]\d{2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}",
                line
            )

            amount = re.search(
                r"-?\d[\d,]*\.?\d{2}",
                line
            )

            if date and amount:

                d = date.group(0)
                a = amount.group(0).replace(",", "")

                desc = (
                    line.replace(d, "")
                        .replace(amount.group(0), "")
                        .strip()
                )

                parsed.append({
                    "Date": d,
                    "Description": desc,
                    "Amount": float(a)
                })

        if len(parsed) == 0:
            raise ValueError("Unable to extract transactions from PDF.")

        return pd.DataFrame(parsed)

    @staticmethod
    def find_column(columns, aliases):

        for alias in aliases:
            for col in columns:
                if alias in col.upper():
                    return col

        return None

    @staticmethod
    def map_and_clean_columns(df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

        # Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]

        # Normalize column names
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.upper()
            .str.replace("_", " ")
            .str.replace("-", " ")
        )

        DATE_ALIASES = [
            "DATE",
            "TRANSACTION DATE",
            "VALUE DATE",
            "POSTING DATE",
            "TXN DATE"
        ]

        DESC_ALIASES = [
            "DESCRIPTION",
            "TRANSACTION DETAILS",
            "DETAILS",
            "NARRATION",
            "REMARKS",
            "MERCHANT",
            "PARTICULAR",
            "PAYEE"
        ]

        AMOUNT_ALIASES = [
            "AMOUNT",
            "TRANSACTION AMOUNT",
            "VALUE"
        ]

        DEBIT_ALIASES = [
            "DEBIT",
            "WITHDRAWAL",
            "WITHDRAWAL AMT",
            "DEBIT AMOUNT",
            "DR"
        ]

        CREDIT_ALIASES = [
            "CREDIT",
            "DEPOSIT",
            "DEPOSIT AMT",
            "CREDIT AMOUNT",
            "CR"
        ]

        date_col = DataProcessor.find_column(df.columns, DATE_ALIASES)
        desc_col = DataProcessor.find_column(df.columns, DESC_ALIASES)
        amount_col = DataProcessor.find_column(df.columns, AMOUNT_ALIASES)

        debit_col = DataProcessor.find_column(df.columns, DEBIT_ALIASES)
        credit_col = DataProcessor.find_column(df.columns, CREDIT_ALIASES)

        if date_col is None:
            raise KeyError("Date column not found.")

        if desc_col is None:
            raise KeyError("Description column not found.")

        # Create Amount column

        if amount_col is not None:

            df["Amount"] = pd.to_numeric(
                df[amount_col],
                errors="coerce"
            )

        elif debit_col is not None or credit_col is not None:

            debit = (
                pd.to_numeric(df[debit_col], errors="coerce")
                if debit_col
                else pd.Series(0, index=df.index)
            ).fillna(0)

            credit = (
                pd.to_numeric(df[credit_col], errors="coerce")
                if credit_col
                else pd.Series(0, index=df.index)
            ).fillna(0)

            # Expenses negative, deposits positive
            df["Amount"] = credit - debit

        else:
            raise KeyError("Amount column not found.")

        df = df.rename(columns={
            date_col: "Date",
            desc_col: "Description"
        })

        df = df[["Date", "Description", "Amount"]]

        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce",
            dayfirst=True
        )

        df["Description"] = (
            df["Description"]
            .astype(str)
            .str.strip()
        )

        df["Amount"] = (
            pd.to_numeric(df["Amount"], errors="coerce")
            .fillna(0)
        )

        df = df.dropna(subset=["Date"])

        df = df.sort_values("Date")

        df.reset_index(drop=True, inplace=True)

        return df
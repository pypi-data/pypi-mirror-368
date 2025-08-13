import pandas as pd

class DataQualityChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.results = {}

    def check_column(self, column: str, checks: list):
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found")

        col_results = []
        for check in checks:
            result = check(self.df[column])
            # Attach failing row details
            if result["failed_rows"]:
                failed_rows_df = self.df.loc[result["failed_rows"], [column]].reset_index()
                failed_examples = failed_rows_df.head(5).to_dict(orient="records")  # first 5 failures
            else:
                failed_examples = []
            result["failed_examples"] = failed_examples
            col_results.append(result)

        self.results[column] = col_results

    def run(self, rules: dict):
        for col, checks in rules.items():
            self.check_column(col, checks)
        return self.results

    def generate_report(self):
        lines = ["\n=== DATA QUALITY REPORT ==="]
        for column, checks in self.results.items():
            lines.append(f"\nColumn: {column}")
            for c in checks:
                status = "✅ PASS" if c["passed"] else "❌ FAIL"
                lines.append(f"  - {c['name']}: {status} | {c['message']}")
                if not c["passed"] and c["failed_examples"]:
                    lines.append("    Examples of failures:")
                    for ex in c["failed_examples"]:
                        lines.append(f"      Row {ex['index']}: {column} = {ex[column]}")
        return "\n".join(lines)

    def export_report(self, path="validata_report.csv"):
        rows = []
        for column, checks in self.results.items():
            for c in checks:
                rows.append({
                    "column": column,
                    "check": c["name"],
                    "status": "PASS" if c["passed"] else "FAIL",
                    "message": c["message"],
                    "failed_examples": c["failed_examples"]
                })
        pd.DataFrame(rows).to_csv(path, index=False)

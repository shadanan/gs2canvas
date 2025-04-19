import argparse
import re
from io import StringIO

import pandas as pd
import rich
from rich.table import Table

STUDENT_DB_COLUMNS = ["SIS Login ID", "Student", "Section"]
GS_RESPONSE_COLUMNS = ["Email Address", "Score"]


def to_kebab_case(text):
    text = re.sub(
        r"([A-Z]+)([A-Z][a-z])", r"\1-\2", text
    )  # Split uppercase followed by uppercase-lowercase
    text = re.sub(
        r"([a-z0-9])([A-Z])", r"\1-\2", text
    )  # Split lowercase/number followed by uppercase
    return text.lower().replace(" ", "-")  # Lowercase and replace spaces with hyphens


def rich_print_df(df, title="DataFrame"):
    table = Table(title=title)
    for column in df.columns:
        table.add_column(str(column))
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row.values])
    rich.print(table)


def load_student_db(buf: StringIO) -> pd.DataFrame:
    sdf = pd.read_csv(buf, skiprows=[1])
    for col in STUDENT_DB_COLUMNS:
        if col not in sdf.columns:
            raise Exception(f"`{col}` is missing")
    return sdf[STUDENT_DB_COLUMNS]


def load_gs_responses(buf: StringIO) -> pd.DataFrame:
    rdf = pd.read_csv(buf)
    for col in GS_RESPONSE_COLUMNS:
        if col not in rdf.columns:
            raise Exception(f"`{col}` is missing")
    return rdf[GS_RESPONSE_COLUMNS]


def save_canvas_import(df: pd.DataFrame, fp=None):
    return df.to_csv(fp, index=False)


def convert_score(score):
    return f"{int(score.split(' / ')[0])}"


def compute_missing_students(sdf: pd.DataFrame, rdf: pd.DataFrame) -> pd.DataFrame:
    mdf = rdf.merge(sdf, how="left", left_on="Email Address", right_on="SIS Login ID")
    return mdf[mdf["SIS Login ID"].isnull()][GS_RESPONSE_COLUMNS]


def compute_canvas_import(
    sdf: pd.DataFrame, rdf: pd.DataFrame, name: str
) -> pd.DataFrame:
    cdf = pd.merge(rdf, sdf, left_on="Email Address", right_on="SIS Login ID")
    cdf[name] = cdf["Score"].apply(lambda score: int(score.split(" / ")[0]))
    cdf = cdf[["Student", "SIS Login ID", "Section", name]]
    header = pd.DataFrame(
        [
            {
                "Student": "    Points Possible",
                "SIS Login ID": "",
                "Section": "",
                name: int(rdf.iloc[0]["Score"].split(" / ")[1]),
            }
        ]
    )
    return pd.concat([header, cdf]).reset_index(drop=True)


def process(*, db: StringIO, gs: StringIO, name: str, canvas: StringIO):
    sdf = load_student_db(db)
    rdf = load_gs_responses(gs)
    mdf = compute_missing_students(sdf, rdf)
    if len(mdf) > 0:
        rich_print_df(mdf, title="Missing Students")
    cdf = compute_canvas_import(sdf, rdf, name)
    rich_print_df(cdf, title="Canvas Import")
    save_canvas_import(cdf, canvas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db",
        type=argparse.FileType("r"),
        required=True,
        help="A csv file containing a map from student email (SIS Login ID) to student name (Student), typically exported from Canvas.",
    )
    parser.add_argument(
        "--gs",
        type=argparse.FileType("r"),
        required=True,
        help="A csv file containing the scores (Score) of each student (Email Address), typically exported from Google Sheets.",
    )
    parser.add_argument(
        "--canvas",
        type=argparse.FileType("w"),
        default="-",
        help="A file where Canvas importable data will be saved. Defaults to stdout.",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="The name of the assignment or test to use when importing into Canvas.",
    )
    args = parser.parse_args()
    process(db=args.db, gs=args.gs, name=args.name, canvas=args.canvas)


if __name__ == "__main__":
    main()

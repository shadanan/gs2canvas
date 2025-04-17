import argparse
from io import TextIOWrapper

import pandas as pd
import rich
from rich.table import Table


def rich_print_df(df, title="DataFrame"):
    table = Table(title=title)
    for column in df.columns:
        table.add_column(str(column))
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row.values])
    rich.print(table)


def load_student_db(buf: TextIOWrapper) -> pd.DataFrame:
    return pd.read_csv(buf, skiprows=[1])[["SIS Login ID", "Student", "Section"]]


def load_gs_responses(buf: TextIOWrapper) -> pd.DataFrame:
    df = pd.read_csv(buf).rename(columns={"Email Address": "SIS Login ID"})
    df = df[["SIS Login ID", "Score", "Your first name", "Your last name"]]
    return df


def convert_score(score):
    return f"{int(score.split(' / ')[0])}"


def log_unknown_students(sdf: pd.DataFrame, rdf: pd.DataFrame):
    known_students = set(sdf["SIS Login ID"])
    test_students = set(rdf["SIS Login ID"])
    unknown_students = test_students - known_students
    if len(unknown_students) > 0:
        rich_print_df(
            rdf[rdf["SIS Login ID"].isin(unknown_students)], title="Unmapped Students"
        )


def convert(sdf: pd.DataFrame, rdf: pd.DataFrame, name: str) -> pd.DataFrame:
    cdf = pd.merge(rdf, sdf, on="SIS Login ID")
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


def process(*, db: TextIOWrapper, gs: TextIOWrapper, name: str, canvas: TextIOWrapper):
    sdf = load_student_db(db)
    rdf = load_gs_responses(gs)
    log_unknown_students(sdf, rdf)
    cdf = convert(sdf, rdf, name)
    rich_print_df(cdf, title="Canvas Data")
    cdf.to_csv(canvas, index=False)


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
        help="A file containing the scores (Score) of each student (Email Address), typically exported from Google Sheets.",
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

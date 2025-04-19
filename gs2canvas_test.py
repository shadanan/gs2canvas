import pytest

import gs2canvas


def test_load_student_db_succeeds():
    with open("data/student_db.csv") as fp:
        gs2canvas.load_student_db(fp)


def test_load_student_db_missing_col_throws():
    with open("data/gs_responses.csv") as fp:
        with pytest.raises(Exception):
            gs2canvas.load_student_db(fp)


def test_load_gs_responses_succeeds():
    with open("data/gs_responses.csv") as fp:
        gs2canvas.load_gs_responses(fp)


def test_load_gs_responses_missing_col_throws():
    with open("data/student_db.csv") as fp:
        with pytest.raises(Exception):
            gs2canvas.load_gs_responses(fp)


def test_compute_missing_students_succeeds():
    with open("data/student_db.csv") as fp:
        sdf = gs2canvas.load_student_db(fp)
    with open("data/gs_responses.csv") as fp:
        rdf = gs2canvas.load_gs_responses(fp)

    mdf = gs2canvas.compute_missing_students(sdf, rdf)

    actual = mdf.to_csv(index=False)
    with open("data/missing_students.csv") as fp:
        expected = fp.read()
    assert actual == expected


def test_compute_canvas_import_succeeds():
    with open("data/student_db.csv") as fp:
        sdf = gs2canvas.load_student_db(fp)
    with open("data/gs_responses.csv") as fp:
        rdf = gs2canvas.load_gs_responses(fp)

    cdf = gs2canvas.compute_canvas_import(sdf, rdf, "Test 2")

    actual = gs2canvas.save_canvas_import(cdf)
    with open("data/canvas_import.csv") as fp:
        expected = fp.read()
    assert actual == expected

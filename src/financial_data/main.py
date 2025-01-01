from prefect import flow

from .collect import parse_bcs_courses, parse_tinkoff_courses
from .preprocessing import (
    clear_txt,
    index_chunks,
    pdf2txt,
    process_3d_party_data,
    split_documents,
)


@flow
def collect_data() -> None:
    parse_bcs_courses()
    parse_tinkoff_courses()
    return None


@flow
def clear_data() -> None:
    clear_txt()
    process_3d_party_data()
    split_documents()
    index_chunks()
    return None


if __name__ == "__main__":
    collect_data()
    pdf2txt()
    clear_data()

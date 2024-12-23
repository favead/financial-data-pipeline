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
def run_pipeline() -> None:
    parse_bcs_courses(),
    parse_tinkoff_courses()
    pdf2txt()
    clear_txt()
    process_3d_party_data()
    split_documents()
    index_chunks()
    return None


if __name__ == "__main__":
    run_pipeline()

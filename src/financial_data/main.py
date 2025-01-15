from .collect import parse_bcs_courses, parse_tinkoff_courses
from .evaluate import collect_data_quality_metrics, collect_eda_metrics
from .preprocessing import (
    clear_txt,
    create_configs,
    html2txt,
    index_chunks,
    pdf2txt,
    process_3d_party_data,
    split_documents,
)


def collect_data() -> None:
    parse_bcs_courses()
    parse_tinkoff_courses()
    return None


def transform_data() -> None:
    html2txt()
    pdf2txt()
    return None


def process_data() -> None:
    create_configs()
    clear_txt()
    process_3d_party_data()
    split_documents()
    return None


def collect_metrics() -> None:
    collect_data_quality_metrics()
    collect_eda_metrics()
    return None


if __name__ == "__main__":
    collect_data()
    transform_data()
    process_data()
    collect_metrics()
    index_chunks()

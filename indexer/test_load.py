from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.documents.base import Document

from src.load import load


def main() -> None:
    load_dotenv()
    load(
        {
            "snapshot_Test": [
                Document(
                    page_content="snapshot test",
                    metadata={"source": "test_load.py"},
                    id=str(uuid4()),
                )
            ]
        }
    )


if __name__ == "__main__":
    main()

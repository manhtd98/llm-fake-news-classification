import dotenv

dotenv.load_dotenv()
import logging
import pandas as pd
from glob import glob
from tqdm import tqdm
from rag_query import get_chain
from logger_helper import configure_logging
from config import CONFIG

configure_logging()


def main():
    all_data = []
    for file in glob("./test/*.xlsx"):
        df = pd.read_excel(file, index_col=0)
        all_data.append(df)
    df_merge = pd.concat(all_data)
    df_merge["predict"] = ""

    QA_CHAIN = get_chain()
    for index, row in tqdm(df_merge.iterrows()):
        response = QA_CHAIN(row[0])
        logging.info(response["result"])
        df_merge.at[index, "predict"] = str(response["result"])
    df_merge.to_csv(
        f"output_{CONFIG.LLM_MODEL_ID}_{CONFIG.EMBEDDING_MODEL_ID}.csv", index=False
    )
    return 0


if __name__ == "__main__":
    main()

from typing import Sequence

import pandas as pd
import numpy as np
import datetime
from snowflake.connector.cursor import ResultMetadata
from snowflake.connector.constants import FIELD_ID_TO_NAME

def format_columns(result_frame:pd.DataFrame, result_metadata:Sequence[ResultMetadata]) -> pd.DataFrame:
    for i, col in enumerate(result_frame.columns):
        col_metadata = result_metadata[i]
        if result_frame[col].apply(lambda x: isinstance(x, (datetime.date, datetime.datetime))).any():
            result_frame[col] = pd.to_datetime(result_frame[col], errors='coerce')
        elif FIELD_ID_TO_NAME[col_metadata.type_code] == "FIXED" and col_metadata.scale == 0:
            result_frame[col] = result_frame[col].astype('Int64')
    result_frame = result_frame.replace({None: np.nan})
    return result_frame
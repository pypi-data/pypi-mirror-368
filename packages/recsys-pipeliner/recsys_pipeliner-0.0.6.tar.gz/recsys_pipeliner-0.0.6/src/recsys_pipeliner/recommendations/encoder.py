from __future__ import annotations # required for sagemaker local mode
import pandas as pd
from sklearn.preprocessing import LabelEncoder



def encode_labels(
    df: pd.DataFrame, user="user_id", item="item_id"
) -> tuple[pd.DataFrame, LabelEncoder, LabelEncoder]:
    user_encoder = LabelEncoder()
    item_encoder = LabelEncoder()

    df[user] = user_encoder.fit_transform(df[user])
    df[item] = item_encoder.fit_transform(df[item])

    return df, user_encoder, item_encoder

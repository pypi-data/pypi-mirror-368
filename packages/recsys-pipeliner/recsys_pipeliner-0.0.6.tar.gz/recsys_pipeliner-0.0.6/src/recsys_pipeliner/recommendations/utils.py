from __future__ import annotations # required for sagemaker local mode
import pandas as pd
import numpy as np


def train_test_split(
    df: pd.DataFrame,
    min_user_ratings=5,
    interaction_cap=5,
    test_sample_size=1,
    test_sample_strategy="tail"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    MIN_USER_RATINGS = min_user_ratings
    INTERACTION_CAP = interaction_cap

    unique_users, unique_user_counts = np.unique(df.user_id, return_counts=True)
    excluded_users = unique_users[unique_user_counts < MIN_USER_RATINGS]

    test_train_data_df = df[~df.user_id.isin(excluded_users)].sort_values(
        by=["date", "user_id"], ascending=True
    )

    test_data_df = (
        test_train_data_df.reset_index()
        .groupby(["user_id"], as_index=False)
        .last()
        .set_index("index")
    )[["user_id", "item_id"]]
    test_data_df.index.names = [None]

    train_data_df = (
        test_train_data_df[~test_train_data_df.index.isin(test_data_df.index)]
        .groupby(["user_id", "item_id"])
        .agg({"interactions": "sum"})
        .reset_index()
    )

    ratings = np.minimum(train_data_df.interactions, INTERACTION_CAP).astype(np.int32)
    ratings = 1 + np.log1p(ratings)
    ratings = (ratings / ratings.max()).round(5)

    train_data_df["rating"] = ratings

    train_data_df = train_data_df[["user_id", "item_id", "rating"]]

    return train_data_df, test_data_df

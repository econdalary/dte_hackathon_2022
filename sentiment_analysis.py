import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

DATA_BASE_PATH = "./data"


if __name__ == "__main__":
    # read in datasets
    users = pd.read_excel(f"{DATA_BASE_PATH}/tweets.xlsx", sheet_name="users")
    tweets = pd.read_excel(f"{DATA_BASE_PATH}/tweets.xlsx", sheet_name="tweets")
    storms = pd.read_csv(f"{DATA_BASE_PATH}/storms.csv")

    # select correct columns"
    tweets = tweets[
        ["Tweet Id", "Name", "UTC", "Favorites", "Retweets", "Text"]
    ].rename(
        columns={
            "Tweet Id": "tweet_id",
            "Name": "user",
            "UTC": "tweet_date",
            "Favorites": "count_favorites",
            "Retweets": "count_retweets",
            "Text": "text",
        }
    )
    users = users[["Name", "Followers", "Tweets", "Verified", "Location"]].rename(
        columns={
            "Followers": "count_followers",
            "Tweets": "count_all_tweets",
            "Verified": "is_verified",
            "Location": "location",
        }
    )

    # combine datasets on cols
    final = pd.concat([tweets, users], axis=1)

    # add tweet_month and tweet_year
    final["tweet_date"] = pd.to_datetime(final["tweet_date"])
    final["tweet_month"] = final["tweet_date"].dt.month
    final["tweet_year"] = final["tweet_date"].dt.year

    # parse out city
    final["city"] = final["location"].str.split(",", expand=True, n=1)[0]
    final.to_csv("data/preproc.csv")

    # aggregate storm info
    storms = storms.loc[
        storms["Associated Storm"].notna(),
        ["Associated Storm Start", "Customers Affected* (GraySky)"],
    ].rename(
        columns={
            "Associated Storm Start": "tweet_date",
            "Customers Affected* (GraySky)": "customers_affected",
        }
    )
    storms["tweet_date"] = pd.to_datetime(storms["tweet_date"])
    storms["tweet_month"] = storms["tweet_date"].dt.month
    storms["tweet_year"] = storms["tweet_date"].dt.year
    storms["customers_affected"] = (
        storms["customers_affected"].str.replace(",", "").astype(float)
    )
    storms_aggd = (
        storms.groupby(["tweet_month", "tweet_year"])
        .agg(["count", "sum"])
        .reset_index()
    )
    storms_aggd.columns = [f"{i}_{k}" for i, k in storms_aggd.columns.to_flat_index()]
    storms_aggd.rename(
        columns={
            "tweet_month_": "tweet_month",
            "tweet_year_": "tweet_year",
            "customers_affected_sum": "total_affected_customers",
            "customers_affected_count": "number_of_storms",
        },
        inplace=True,
    )
    storms_aggd["average_affected_customers"] = (
        storms_aggd["total_affected_customers"] / storms_aggd["number_of_storms"]
    )
    storms_aggd.to_csv("data/storms_aggd.csv")

    # last merge!
    final = pd.merge(final, storms_aggd, on=["tweet_month", "tweet_year"])
    final.to_csv("data/cleaned_up.csv")  # TODO what's wrong here?

    # TODO scoring of tweet text
    tokenizer = AutoTokenizer.from_pretrained("model")
    model = AutoModelForSequenceClassification.from_pretrained("model")
    classifier = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
        return_all_scores=True,
    )
    # prediction = classifier(
    #     "I love using transformers. The best part is wide range of support and its easy to use",
    # )
    # print(prediction)

    # TODO choose the max of scores as the sentiment_label

    # output file to csv

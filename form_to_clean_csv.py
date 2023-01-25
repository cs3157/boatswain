import pandas as pd
import sys

# usage: [form.csv] [hw_number]
# creates 2 files hw_number_handles.csv & hw_number_teams.csv

data = pd.read_csv(sys.argv[1])
df = pd.DataFrame(data)

df = pd.DataFrame(data)
df["Group Name"] = df.index.astype(str) + "_" + df["Group Name"]

df1 = df[["Group Name", "UNI", "GitHub Handle"]]
df2 = df[["Group Name", "UNI.1", "GitHub Handle.1"]].rename(columns={"UNI.1": "UNI", "GitHub Handle.1": "GitHub Handle"})
df3 = df[["Group Name", "UNI.2", "GitHub Handle.2"]].rename(columns={"UNI.2": "UNI", "GitHub Handle.2": "GitHub Handle"})

union_dfs = pd.concat([df1, df2, df3]).dropna()

union_dfs.to_csv(sys.argv[2] + "_handles.csv", index=False)

df_groups = df[["Group Name", "GitHub Handle", "GitHub Handle.1", "GitHub Handle.2"]]

df_groups.to_csv(sys.argv[2] + "_teams.csv", index=False)
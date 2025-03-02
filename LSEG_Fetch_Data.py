import pandas as pd
import lseg.data as ld
from lseg.data.content.historical_pricing import summaries





# Open the session. This few lines could be removed in later commits as session could be opened separately by user even though it's a prerequisite

session = ld.open_session(
    name="platform.ldp",
    config_name="" #here you need to enter the file path where the config.json config script is 
)


start_date = "2024-01-01"
end_date = "2024-12-31"
universe = [".SPX", ".NDX"]

definition = summaries.Definition(
    universe=universe,
    interval="P1D",
    start=start_date,
    end=end_date,
    fields=["TRDPRC_1"]
)


data = definition.get_data()

extracted_data = data._data_raw  


df_list = []
for entry in extracted_data:
    df = pd.DataFrame(entry['data'], columns=['Date', entry['universe']['ric']])
    df_list.append(df)

# Merge the data into a single DataFrame
df_final = df_list[0]
for df in df_list[1:]:
    df_final = df_final.merge(df, on='Date', how='outer')


df_final['Date'] = pd.to_datetime(df_final['Date'])


df_final = df_final.sort_values('Date').reset_index(drop=True)

spx_data = df_final[["Date", ".SPX"]].copy()

ndx_data = df_final[["Date", ".NDX"]].copy()



print(spx_data, "\n", ndx_data) 









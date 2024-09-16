import pandas as pd

# file_df = pd.read_excel("data_2018_complete.xlsx")
file_df = pd.read_excel("Complete_2019.xlsx")


# Keep only FIRST record from set of duplicates
file_df_first_record = file_df.drop_duplicates(subset=["link","id"], keep="first")
file_df_first_record.to_excel("cleaned_data_2019.xlsx", index=False)

# # Keep only LAST record from set of duplicates
# file_df_last_record = file_df.drop_duplicates(subset=["Name", "Address", "Call Date"], keep="last")
# file_df_last_record.to_excel("Duplicates_Last_Record.xlsx", index=False)

# # Remove ALL records of a set of duplicates
# file_df_remove_all = file_df.drop_duplicates(subset=["Name", "Address", "Call Date"], keep=False)
# file_df_remove_all.to_excel("Duplicates_All_Removed.xlsx", index=False)

# # Find what the duplicate were
# duplicate_row_index = file_df.duplicated(subset=["Name", "Address", "Call Date"], keep="first")
# all_duplicate_rows = file_df[duplicate_row_index]
# duplicate_rows = all_duplicate_rows.drop_duplicates(subset=["Name", "Address", "Call Date"], keep="first")
# duplicate_rows.to_excel("Duplicate_Rows.xlsx", index=False)
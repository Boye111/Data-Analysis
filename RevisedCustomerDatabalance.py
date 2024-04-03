import pandas as pd
import zipfile
import requests
from datetime import datetime

# Function to download CSV file from the provided link
def download_csv_from_link(download_link):
    try:
        response = requests.get(download_link)
        if response.status_code == 200:
            # Save the downloaded content to a file
            zip_file_path = 'temp.zip'
            with open(zip_file_path, 'wb') as f:
                f.write(response.content)
            return zip_file_path
        else:
            print("Failed to download CSV from the provided link.")
            return None
    except Exception as e:
        print(f"Error occurred while downloading CSV: {e}")
        return None

# Function to dynamically change the seconds part of the link until a successful download is made
def get_csv_download_link():
    base_url = "http://**.**.***/Customer_data_balance/Customer_data_balance_{}_{}.zip"
    current_date = datetime.now().strftime('%Y%m%d')
    seconds_part = "060001"
    for i in range(5):
        download_link = base_url.format(current_date, seconds_part)
        print(download_link)
        zip_file_path = download_csv_from_link(download_link)
        if zip_file_path:
            return zip_file_path
        # Incrementing seconds part
        seconds_part = f"06000{i + 4}"  # e.g., 3, 4, 5, ...
    return None
# Get CSV download link and download CSV
zip_file_path = get_csv_download_link()
if zip_file_path:
    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Extract the CSV file
        csv_filename = zip_ref.namelist()[0]  # Assuming there's only one file in the zip
        zip_ref.extract(csv_filename, path='temp_folder')  # Extract to a temporary folder

    # Read the CSV file using Pandas
    df = pd.read_csv(f'temp_folder/{csv_filename}', low_memory=False)

    df['VALID_TO'] = pd.to_datetime(df['VALID_TO'], dayfirst=True, errors='coerce')
    df['VALID_TO'] = df['VALID_TO'].dt.date
    present_date = datetime.now().date()
    filtered_df = df[
        (
            df['resource_name'].str.contains('Day_Bundle_Data_Bank|Promo_24Hours_Data_Bank', case=False)
        ) & (
            (
                (df['VALID_TO'] >= present_date) |
                (df['VALID_TO'] == pd.to_datetime('1970-01-01', errors='coerce')) |
                (pd.isna(df['VALID_TO'])) |
                (pd.isnull(df['VALID_TO']))
            )
        )
    ]
    pivot_table = filtered_df.pivot_table(index='USERID', values='DataBank_Balance_in_GB', aggfunc='sum')
    pivot_table.reset_index(inplace=True)
    pivot_table['DataBank_Balance_in_GB'] *= -1
    pivot_table['DataBank_Balance_in_GB'] = pivot_table['DataBank_Balance_in_GB'].apply(lambda x: max(0, x))
    current_date = datetime.now().strftime('%d%m%Y')
    variable_name = f"customer_databalance{current_date}"
    globals()[variable_name] = pivot_table

    # Save the analyzed DataFrame to a CSV file
    csv_file_path = f'D:/Users/System/Documents/Python CSV/Customer DataBalance/{csv_filename}'
    pivot_table.to_csv(csv_file_path, index=False)
    print(f"CSV file saved at: {csv_file_path}")

    # Print the DataFrame to verify
    print(pivot_table)
else:
    print("Unable to download CSV from the provided link.")

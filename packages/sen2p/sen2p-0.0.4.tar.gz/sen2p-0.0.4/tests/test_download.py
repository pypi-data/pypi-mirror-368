from sen2p import download
location =[172.0, -43.6, 172.5, -43.3]
# Call the function
results = download(
    start_date="2016-09-01",
    end_date="2016-09-10",
    location=location,
    bands=["B02","B03","B04"],
    output_dir="Downloads",
    merge_bands=True,
    max_items=None 
)
from google.cloud.bigquery import client
from google.cloud import bigquery
import os

def csv_to_bq(filename, dataset_id, table_id, overwrite=True, auto=True):
    """
    return : overwrite to : WRITE_APPEND if append
    """
    from google.cloud.bigquery import client
    from google.cloud import bigquery
    import os
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'plex-analysis-2020-f83a7fba4dc7.json'
    client = bigquery.Client()
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    if auto:
        job_config.autodetect = True
    else:
        job_config.schema = [bigquery.SchemaField("productSKU", "STRING"),
            bigquery.SchemaField("productName", "STRING"), bigquery.SchemaField("productPrice", "FLOAT"),
            bigquery.SchemaField("date", "DATE"), bigquery.SchemaField("categories", "STRING"),
            bigquery.SchemaField("ratios", "STRING"), bigquery.SchemaField("productPricePerGram", "FLOAT"),
            bigquery.SchemaField("productUnit", "STRING")]

    if overwrite:
        job_config.write_disposition = 'WRITE_TRUNCATE'
    else:
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

    with open(filename, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
    job.result()  # Waits for table load to complete.
    print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, table_id))
    return

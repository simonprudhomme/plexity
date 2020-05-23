import schedule
import time
try:
    from app.a_scraper import main_scraper
    from app.b_preprocessing import main_preprocessing
    from app.c_calculator_upload import main_calculation_and_upload
    from app.e_send_message import text_people
except:
    from a_scraper import main_scraper
    from b_preprocessing import main_preprocessing
    from c_calculator_upload import main_calculation_and_upload
    from e_send_message import text_people

#1. define job
def job():
    tic = time.perf_counter()
    main_scraper()
    main_preprocessing()
    main_calculation_and_upload()
    toc = time.perf_counter()
    time_total = round(((toc - tic) / 60))
    text_people(f"Plexity just update DB. Getting job done in {time_total} minutes")
    return

# #2. Run job
# Run job evey day
#schedule.every().day.at("01:00").do(job,'It is 01:00')

#while True:
#    schedule.run_pending()
#    time.sleep(1) # wait one minute
#job()

main_calculation_and_upload()
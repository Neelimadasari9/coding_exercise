import datetime, os
import logging

logging.basicConfig(filename="logs/record.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)


def read_wx_data():
    print("Reading wx Data...")
    weather = []
    path = f"{os.getcwd()}/wx_data"
    from .app import WeatherRecord

    for file in os.listdir(path):
        if file.endswith(".txt"):
            print("reading file:", file)
            fpath = f"{path}/{file}"
            with open(fpath, "r") as data:
                lines = [line.rstrip() for line in data]
                for line in lines:
                    temp = line.split("\t")
                    w = WeatherRecord(
                        station=file[:-4],
                        date=int(temp[0]),
                        maximum_temperature=int(temp[1]),
                        minimum_temperature=int(temp[2]),
                        precipitation=int(temp[3]),
                    )
                    weather.append(w)
    print(f"Weather File read complete: found {len(weather)} records")
    return weather


def ingest_wx_data():
    from .app import db

    initial_time = datetime.datetime.now()

    weather = read_wx_data()
    s = db.session
    print("data saving to database ........")
    s.bulk_save_objects(weather)
    s.commit()
    logger.info("weather data loaded..")
    completion_time = datetime.datetime.now()
    logger.info(
        f"Weather Data inserted in : {(completion_time-initial_time).total_seconds()} secs \t Total rows: {len(weather)}"
    )
    print("data inserted")


def generate_statistics():
    from .app import db

    query = """
            INSERT INTO statistic(station, date,  final_maximum_temperature, final_minimum_temperature, final_precipitation)
            SELECT station,date, avg(maximum_temperature),avg(minimum_temperature), sum(precipitation)
                from (
                    select * from weather_record
                    where maximum_temperature!=-9999
                    and minimum_temperature!=-9999
                    and precipitation!=-9999
                ) group by station , substring(date,1,4)
            """
    s = db.session
    s.execute(query)
    s.commit()
    logger.info("statistics data loaded...")

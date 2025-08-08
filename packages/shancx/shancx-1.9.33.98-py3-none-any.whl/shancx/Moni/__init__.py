import os
import time
import shutil
import datetime
from dateutil.relativedelta import relativedelta
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# from config import logger
from shancx.NN import _loggers
logger = _loggers()
import traceback
import netCDF4 as nc
import pandas as pd 
from watchdog.observers.polling import PollingObserver

def wait(path,sepSec,timeoutSec,debug=False):
    t0 = datetime.datetime.now()
    t1 = datetime.datetime.now()
    flag= True
    while flag:
        if (t1-t0).total_seconds()>timeoutSec:
            flag =False
            break
        else:
            if os.path.exists(path):
                try:
                    if path.endswith("nc") or path.endswith("NC"):
                        with nc.Dataset(path) as dataNC:
                            a = dataNC[list(dataNC.variables.keys())[-1]][:]
                    else:
                        pass

                    flag =False
                    return True
                except Exception as e:
                    logger.error(traceback.format_exc())
                    logger.error(f"wrong data{path}")

            if not debug:
                logger.info(f"{path} missing  waiting {sepSec}s {int(timeoutSec-(t1-t0).total_seconds())}s remain")
                time.sleep(sepSec)
            else:
                logger.info(f"{path} missing  break")
                return False
            t1 = datetime.datetime.now()

    if not flag:
        return False
    else:
        return True

import os
import time

def is_file_stable(file_path, check_interval=6, max_unchanged_checks=3):
    """
    判断文件是否不再增长
    :param file_path: 文件路径
    :param check_interval: 检查间隔（秒）
    :param max_unchanged_checks: 连续多少次大小未变化视为稳定
    :return: True（文件稳定）/ False（文件可能仍在写入）
    """
    last_size = -1
    unchanged_checks = 0

    while unchanged_checks < max_unchanged_checks:
        current_size = os.path.getsize(file_path)
        if current_size == last_size:
            unchanged_checks += 1
        else:
            unchanged_checks = 0
            last_size = current_size
        time.sleep(check_interval)
    return True
def gtr(sUTC,eUTC, freq='6min'):
    minute = sUTC.minute
    if minute in [15, 45]:
        start_time = sUTC + relativedelta(minutes=3)  # 15 或 45 分钟时，起始点加 3 分钟
    elif minute in [0, 30]:
        start_time = sUTC + relativedelta(minutes=6)  # 0 或 30 分钟时，起始点加 6 分钟
    else:
        raise ValueError("sUTC 的分钟数必须是 0、15、30 或 45 分钟")
    new_times = pd.date_range(start_time, eUTC, freq=freq)
    # new_times,new_timess =  Unew_times(new_times)
    return new_times 

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = None  # 初始为None，表示无事件发生
        self.latest_file = None
    def on_created(self, event):
        if not event.is_directory:
            self.last_modified = time.time()  # 仅在实际事件发生时更新
            self.latest_file = event.src_path
            logger.info(f"New file: {event.src_path}")
    def on_modified(self, event):
        if not event.is_directory:
            self.last_modified = time.time()  # 仅在实际事件发生时更新
            self.latest_file = event.src_path
            logger.debug(f"Modified file: {event.src_path}")
    def check_for_idle(self, idle_time=5):
        if self.last_modified is None:
            return False  # 无事件发生时，始终返回False
        return time.time() - self.last_modified > idle_time
def start_monitoring(paths,ty="O"):
    event_handler = MyHandler()
    observer = Observer()  
    observer = Observer() if ty=="O" else PollingObserver() # 替换 Observer()   PollingObserver() 
    for path in paths:
        observer.schedule(event_handler, path, recursive=True)    
    observer.start()    
    try:
        while True:
            if event_handler.check_for_idle():
                if True:
                    sepSec = 3
                    timeoutSec = 30
                    isDebug = False
                    latestpath = event_handler.latest_file.split(".nc")[0] + ".nc"
                    flag = wait(latestpath, sepSec, timeoutSec,isDebug)
                    if flag:
                        print()
                        Strptime = event_handler.latest_file.split("_")[-1][:-3]
                        dt = datetime.datetime.strptime(Strptime, '%Y%m%d%H%M%S')
                        UTCStr = dt.strftime("%Y%m%d%H%M%S")
                        command = f"cd /mnt/wtx_weather_forecast/scx/mqpf_FY4B/ && /home/scx/miniconda3/envs/mqpf/bin/python mainFY4B.py --times {UTCStr[:12]} --isDebug --sepSec 360 --gpu 3"
                        os.system(command)
                # if True:
                #     sepSec = 3
                #     timeoutSec = 30
                #     isDebug = False
                #     latestpath = event_handler.latest_file 
                #     if is_file_stable(latestpath):
                #         Strptime = event_handler.latest_file.split("_")[-4]
                #         dt = datetime.datetime.strptime(Strptime, '%Y%m%d%H%M%S')
                #         UTC = (dt + relativedelta(minutes = 15))
                #         times= gtr(dt,UTC, freq='6min')  
                #         UTCStr = times[0].strftime("%Y%m%d%H%M%S")
                #         radarPath = f"{RadarPath}/{UTCStr[:4]}/{UTCStr[:8]}/RADAR_FY4B_2.0_{UTCStr[:12]}00.nc"
                #         if not os.path.exists(radarPath):
                #             UTCStr = UTC.strftime("%Y%m%d%H%M%S")
                #             command = f"cd /mnt/wtx_weather_forecast/scx/product_log/code06_re2/exam/SatEng/ && /home/scx/miniconda3/envs/mqpf/bin/python mkSRB.py --times {UTCStr[:12]}"
                #             os.system(command)
            time.sleep(1)            
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    BASE_SRC_PATHS = [
    # "/mnt/wtx_weather_forecast/GeoEnvData/rawData/FYDATA/FY4/FY4B/AGRI/L1/FDI/DISK/4000M/2025",
    "/mnt/wtx_weather_forecast/scx/WTX_DATA/RADA/MQPF_FY4B",]
    event_handler = start_monitoring(BASE_SRC_PATHS)


 
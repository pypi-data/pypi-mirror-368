 
import os
import time
import shutil
import datetime
from dateutil.relativedelta import relativedelta
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from shancx.NN import _loggers
logger=_loggers()
#from hjnwtx.mkNCHJN import mkDir
from shancx import crDir
from shancx import Mul_sub

BASE_ORIGIN_PATH = "/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF_FUSI"
BASE_TARGET_PATH = "/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF"
def get_utc_str():
    utc_time = datetime.datetime.utcnow()
    # utc_time = utc_time + relativedelta(minutes=-15)
    utc_time = utc_time + relativedelta(minutes=-6)
    return utc_time.strftime("%Y%m%d%H%M")

def get_sourcePATHS(UTCstr):  
    filePATH =f"{BASE_ORIGIN_PATH}/{UTCstr[:4]}/{UTCstr[:8]}/*" 
    paths = glob.glob(filePATH)
#    paths = [i for i in paths if "PHASE" in i ]
    paths = [i for i in paths if "PHASE" in i and not os.path.exists(get_targetPATHS(i)) ]
    return paths
def get_targetPATHS(path):
    basename = os.path.basename(path)
    UTCstr = basename.split("_")[6]
    trargetPATH =f"{BASE_TARGET_PATH}/{UTCstr[:4]}/{UTCstr[:8]}/{basename}" 
    return trargetPATH     
class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
    def on_modified(self, event):
        if "PHASE" in event.src_path:
            self.last_modified = time.time()
            print(f"文件 {event.src_path} 被修改！")
    # def on_modified(self, event):
    #     self.last_modified = time.time()
    def on_created(self, event):
        if "PHASE" in event.src_path:
            print(f"文件 {event.src_path} 被创建！")
    def on_deleted(self, event):
        if "PHASE" in event.src_path:
            print(f"文件 {event.src_path} 被删除！")
    def check_for_idle(self, idle_time=3):
        if time.time() - self.last_modified > idle_time:
            return True
        return False
def copyF(conf):
    path = conf[0]
    # for path in paths:
    tarpath  = get_targetPATHS(path)
    crDir(tarpath)            
    if not os.path.exists(tarpath):  # 检查目标文件是否已存在
        try:
            shutil.copy2(path, tarpath)
            logger.info(f"copy2 file from {path} to {tarpath}")
        except Exception as e:
            logger.error(f"copy2 file from {path} to {tarpath}")
    else:
          logger.info(f"File {tarpath} already exists, skipping move.") 
def move_files(utc_str):
    paths  = get_sourcePATHS(utc_str)
    if paths:
       Mul_sub(copyF,[paths],6)
def start_monitoring(path):
    event_handler = MyHandler()
    observer = Observer()    
    observer.schedule(event_handler, path, recursive=True)    
    observer.start()    
    try:
        while True:
            if event_handler.check_for_idle(): 
                UTCstr= get_utc_str()
                move_files(UTCstr)                            
            time.sleep(3)            
    except KeyboardInterrupt:
        observer.stop()        
    observer.join()

if __name__ == "__main__":
    start_monitoring(BASE_ORIGIN_PATH)
 

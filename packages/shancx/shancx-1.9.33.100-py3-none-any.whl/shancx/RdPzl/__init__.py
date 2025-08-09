 

def start_points(size, split_size, overlap=0.0): 
    stride = int(split_size * (1 - overlap))  # 计算步长
    points = [i * stride for i in range((size - split_size) // stride + 1)]   
    if size > points[-1] + split_size:   
        points.append(size - split_size)
    return points



"""
    b = np.zeros(sat_data[0].shape)
    x_point = start_points(sat_data[0].shape[0], 256, 0.14)
    y_point = start_points(sat_data[0].shape[1], 256, 0.14)
    overlap1 = 17
    for x in x_point:
        for y in y_point:
            cliped = sat_data[:, x:x + 256, y:y + 256]
            img1 = cliped[np.newaxis].float()
            img1 = img1.cpu().numpy()
            img1 = np.where(np.isnan(img1), 0, img1)
            img2 = img1.reshape(1, 6, 256, 256).astype(np.float32)  # Ensure correct shape and type
            radarpre = run_onnx_inference(ort_session, img2)
            radarpre = (radarpre * 72).squeeze()
            radarpre[radarpre < 13] = 0
            radarpre = QC_ref(radarpre[None], areaTH=30)[0]

            b[x + overlap1:x + 256, y + overlap1:y + 256] = radarpre[overlap1:, overlap1:]

    return b

"""

"""
import numpy as np
with nc.Dataset(f"/mnt/wtx_weather_forecast/WTX_DATA/RADA/CRMosaic_GLB/{UTCstr[:4]}/{UTCstr[:8]}/CR_NA_{UTCstr[:12]}.nc") as dataNC:
    # 获取 'time' 变量
    CRreg  = dataNC.variables[list(dataNC.variables)[3]][:]   #['time', 'lat', 'lon', 'CR_unQC', 'CR']
    latreg  = dataNC.variables[list(dataNC.variables)[1]][:]  #latmax : 85.05112878   latmin : -85.05112878
    lonreg  = dataNC.variables[list(dataNC.variables)[2]][:]  #lonmin : -179.61702041 lonmax : 179.63297959045173  res 0.0


# 定义大区域和小区域的经纬度范围
lat_min_global, lat_max_global = -90, 90  # 大区域纬度范围
lon_min_global, lon_max_global = -180, 180  # 大区域经度范围

lat_min_local, lat_max_local = 26, 73  # 小区域纬度范围
lon_min_local, lon_max_local = -31, 52  # 小区域经度范围
lat_min_local, lat_max_local = latreg[-1], latreg[0]  # 小区域纬度范围
lon_min_local, lon_max_local = lonreg[0], lonreg[-1]  # 小区域经度范围

# 计算分辨率
resolution = 0.05  # 假设纬度和经度的分辨率相同

CRreg1 = CRreg[0][::5, ::5]

# 计算小区域在大区域中的索引范围
lat_start = int((lat_max_global - lat_max_local) / resolution)
lat_end = lat_start + CRreg1.shape[0]
lon_start = int((lon_min_local - lon_min_global) / resolution)
lon_end = lon_start + CRreg1.shape[1]

mask = ~np.isnan(CRreg1)  #mask = ~np.isnan(CRreg1)
result[lat_start:lat_end:1, lon_start:lon_end][mask] = CRreg1[mask]
"""


"""
def MapReg(nc_file_path, lat_min_local, lat_max_local, lon_min_local, lon_max_local, resolution=0.05):
 
    # 打开 NetCDF 文件
    with nc.Dataset(nc_file_path) as dataNC:
        # 获取变量
        CRreg = dataNC.variables[list(dataNC.variables)[3]][:]  # 数据变量
        latreg = dataNC.variables[list(dataNC.variables)[1]][:]  # 纬度
        lonreg = dataNC.variables[list(dataNC.variables)[2]][:]  # 经度

    # 定义大区域的经纬度范围
    lat_min_global, lat_max_global = -90, 90
    lon_min_global, lon_max_global = -180, 180

    # 提取小区域的数据
    CRreg1 = CRreg[0][::5, ::5]  # 假设对数据进行降采样

    # 计算小区域在大区域中的索引范围
    lat_start = int((lat_max_global - lat_max_local) / resolution)
    lat_end = lat_start + CRreg1.shape[0]
    lon_start = int((lon_min_local - lon_min_global) / resolution)
    lon_end = lon_start + CRreg1.shape[1]

    # 创建大区域网格
    result = np.full((int((lat_max_global - lat_min_global) / resolution),
                      int((lon_max_global - lon_min_global) / resolution)), np.nan)

    # 将小区域数据映射到大区域网格中
    mask = ~np.isnan(CRreg1)
    result[lat_start:lat_end, lon_start:lon_end][mask] = CRreg1[mask]

    return result


"""
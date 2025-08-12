import numpy as np
from .paras import FHEADER_DEF, BHEADER_DEF,F_KEYS, B_KEYS
from .paras import COUNT2V, BLOCK_SIZE, DATA_SIZE, DB_FACTOR


def bheader_decode(header) -> dict:
    '''
    把block_header 中有效信息解码出来,

    output: dict of (date_UTC,time_UTC, lat, lon, seq1, seq2,
                     LINE, POINT, Zukang, V, T, GNSS, SN...)
    '''

    H = header.tobytes()
    
    y =  int.from_bytes(H[18:19],'little')
    m =  int.from_bytes(H[19:20],'little')
    d =  int.from_bytes(H[20:21],'little')
    h =  int.from_bytes(H[21:22],'little')
    s1 = int.from_bytes(H[22:23],'little')
    s2 = int.from_bytes(H[23:24],'little')
    date_UTC = f'{y:02d}{m:02d}{d:02d}'
    time_UTC = f'{h:02d}{s1:02d}{s2:02d}'

    lat = int.from_bytes(H[24:28],'little')
    lat = lat%2**28
    lat = lat//1e6 + (lat%1e6)/1e4 / 60.0

    lon = int.from_bytes(H[28:32],'little')
    lon = lon%2**28
    lon = lon//1e6 + (lon%1e6)/1e4 / 60.0

    seq1 = int.from_bytes(H[32:36],'little')
    seq2 = int.from_bytes(H[36:39],'little')

    LINE = int.from_bytes(H[0:2],'little')    #线号
    POINT = int.from_bytes(H[2:4],'little')   #点号
    Zukang = int.from_bytes(H[4:5],'little')# 阻抗
    V = int.from_bytes(H[5:6],'little')# 电池电压
    T = int.from_bytes(H[6:7],'little')-50# 温度
    GNSS = int.from_bytes(H[16:17],'little')# GNSS状态
    SN = int.from_bytes(H[40:44],'little')

    S_def = {0x00:100,0x08:250,0x10:500,0x18:1000,0x20:2000}
    raw = int.from_bytes(H[14:15],'little')
    if raw in S_def:
        sampling_rate = S_def[raw]
    else:
        sampling_rate = raw
    # DB_def = {0x90:0,0x91:6,0x92:12}
    # print(int.from_bytes(H[15:16],'little'))
    DB = int.from_bytes(H[15:16],'little')

    
    inf_dict = {'date_UTC':date_UTC,
              'time_UTC':time_UTC,
              'lat':f'{lat:012.9f}',
              'lon':f'{lon:013.9f}',
              'seq1':f'{seq1:09d}',
              'seq2':f'{seq2:09d}',
              'LINE':f'{LINE:04d}',
              'POINT':f'{POINT:04d}',
              'Zukang':f'{Zukang:02d}',
              'V':f'{V:02d}',
              'T':f'{T:02d}',
              'GNSS':f'{GNSS:02d}',
              'SN':f'{SN:06d}',
              'sampling_rate':sampling_rate,
              'DB':DB,
              }
    
    return inf_dict

def fheader_decode(header) -> dict:
    '''
    把文件头中有效信息解码出来,

    output: dict of (date_UTC,time_UTC, lat, lon, seq1, seq2,
                     LINE, POINT, Zukang, V, T, GNSS, SN...)
    '''

    H = header
    
    inf1 = bheader_decode(H[:48])
    return inf1

def read_bin_multiple_chn(file_name, dt=1, DB=0,
             dtype=np.float32,FTYPE=np.int32,
             N_CHN=None,
             block_size = BLOCK_SIZE, data_size = DATA_SIZE, header_size=BLOCK_SIZE-DATA_SIZE)-> tuple:
    '''
    读取GDST仪器二进制文件, 多通道文件

    file_name: 文件名
    dt       : 采样率，单位ms
    DB       : 增益率,仅 0, 6 18,24可选
    dtype    : 输出数据流的格式
    FTYPE    : 文件内部格式
    block_size :  单个数据块尺寸，默认512 # float32
    data_size  :  单个数据块数据尺寸，默认500 # float32
    header_size:  单个数据块头文件尺寸，默认12 # float32

    output:[头文件 1d, 数据流([N_CHN, NB, data_size]), 内部头文件[N_CHN,header_size]]
    '''

    with open(file_name, 'rb') as f:
        data_int = np.fromfile(f, dtype=FTYPE)
    # data_float = np.zeros(data_int.shape, dtype=dtype)
    
    BS,DS, HS = block_size,data_size,header_size

    N_BLOCK = len(data_int)//BS
    N_DATA = int(7200/dt)
    assert DS*dt/1000*N_DATA==3600 # 一小时
    N_CHN = N_BLOCK//N_DATA

    # print(N_CHN)

    data_int = data_int.reshape([N_BLOCK, HS+DS])
    # 头文件
    f_header = data_int[0,:]
    # 数据流
    data_float = data_int[1:N_DATA*N_CHN+1,HS:HS+DS]*COUNT2V*DB_FACTOR[DB]
    data_float = data_float.astype(dtype)
    data_float = data_float.reshape([N_DATA, N_CHN,DS])
    data_float = np.transpose(data_float,[1,0,2])

    # block头文件
    headers = data_int[1:N_DATA*N_CHN+1,:HS]
    headers = headers.reshape([N_DATA, N_CHN,HS])
    headers = np.transpose(headers,[1,0,2])
    
    return f_header, data_float, headers

def fill_empty_block(data_float:np.array, headers:np.array,
                     fill_value=0
                    )-> tuple:
    '''
    data_float: 3D data, N_CHN*N_block*data_size
    headers   : 3D data, N_CHN*N_block*header_size
    fill_value: 对未采样部分的填充数值

    output    : 2D data_float filled with 0, N_CHN*(N_block*data_size)
    '''

    nc, nb, nd = data_float.shape
    _,  _,  nh = headers.shape
    print('not finished')
    
    return data_float

def read_bin(file_name, dt=1, DB=0,
             IS_Z_CHN = False,
             fill_value=None, 
             dtype=np.float32,FTYPE=np.int32,
             N_CHN=None,
             block_size = BLOCK_SIZE, data_size = DATA_SIZE, header_size=BLOCK_SIZE-DATA_SIZE)-> tuple:
    '''
    读取GDST仪器二进制文件

    file_name: 文件名
    dt       : 采样率，单位ms
    DB       : 增益率,仅 0, 6 18,24可选
    fill_value: 关机没采集部分的填充格式
    IS_Z_CHN : 是否为单分量仪器,是则数据维度不再有CHN维度

    dtype    : 输出数据流的格式
    FTYPE    : 文件内部格式
    N_CHN     : 通道数, 默认为None, 如果有设置,则数据维度变为N_CHN*N_block*data_size,不再依靠dt判断
    block_size :  单个数据块尺寸，默认512 # float32
    data_size  :  单个数据块数据尺寸，默认500 # float32
    header_size:  单个数据块头文件尺寸，默认12 # float32

    output:(头文件, 数据流, 内部头文件)
    '''

    f_header, data_float, headers = \
        read_bin_multiple_chn(file_name, dt, DB,
             dtype=dtype,FTYPE=FTYPE,
             N_CHN=N_CHN,
             block_size = block_size, data_size = data_size, header_size=header_size)

    # 对没采集状态填充
    if fill_value is not None:
        data_float = fill_empty_block(data_float, headers,fill_value=fill_value)
        
    nc,nb,nd = data_float.shape
    data_float = data_float.reshape([nc, nb*nd])

    if IS_Z_CHN:
        data_float = np.squeeze(data_float)
        headers = np.squeeze(headers)

    return    f_header, data_float, headers

def read_header(file_name, dt=1,
             dtype=np.float32,FTYPE=np.int32,
             block_size = BLOCK_SIZE
             )-> np.array:
    '''
    只读取GDST仪器二进制文件的头文件

    file_name: 文件名
    dt       : 采样率，单位ms
    dtype    : 输出数据流的格式
    FTYPE    : 文件内部格式
    block_size :  单个数据块尺寸，默认512 # float32

    output:头文件（1D）
    '''

    with open(file_name, 'rb') as f:
        data_int = np.fromfile(f, count=block_size, dtype=FTYPE)
    
    return data_int
    
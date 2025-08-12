import os
import numpy as np
import scipy.io as sio
from scipy.signal import buttord, butter, lfilter, welch, windows
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from numpy.fft import fftshift  # 把 welch 生成的 f 对齐到 MATLAB 的 twosided 轴
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Tuple    #标注返回多个值的函数（元组

plt.rcParams["font.family"] = ["SimHei"]    #, "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

@dataclass
class BinData:
    dev_code: int   # 设备编号
    channel_code: int   # 通道编号
    data_code: str  # 数据编号（14 字符 + '\0' 填充）
    tv_sec: int     # 抓包时间（秒部分）
    tv_usec: int    # 抓包时间（微秒部分）
    refractive_index: float # 光纤折射率
    space_resolution: float # 空间分辨率
    frame_freq_hz: float    # 帧率 (Hz)
    sample_interval: float  # 采样间隔 (m)
    sample_data_number: int # 采样点总数
    pos_index_from_origin: int  # 坐标偏移点数
    space_point_num_per_frame: int  # 空间位置点数
    store_frame_num: int    # 样本数目（列数）
    data_length: int        # header之后的数据长度(Bytes)
    process_frame_num: int  # 每个采样块帧数
    cable_code: int         # 线路编号
    data_flag01: int        # 数据标志
    res_dumparr: bytes      # 保留字段（104 字节）
    background_erg: float   # 背景能量
    data_short: np.ndarray  # 原始 int16 数据

    @property   #--公开只读属性，用于datashort数据类型转换--
    def data(self) -> np.ndarray:
        '''将 int16 数据转为 double 并 reshape'''
        arr = self.data_short.astype(np.float64) / 32.0
        return arr.reshape(-1, self.store_frame_num, order='F')

#---公有类---
class BaseProcessor(ABC):
    def __init__(self, input_dir: str=None, output_dir: str=None, dpi: int = 300) -> None:
        self.input_dir  = input_dir
        self.output_dir = output_dir
        self.dpi        = dpi
        os.makedirs(self.output_dir, exist_ok=True)
        self._files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.bin')]

    def run(self) -> None:
        total = len(self._files)
        for idx, fn in enumerate(self._files, start=1):
            path = os.path.join(self.input_dir, fn)
            bin_data = self._read_bin(path)
            processed = self._compute(bin_data)
            self._plot(processed, idx, fn)
            print(f"[{idx}/{total}] {fn} 完成")
        self._post_run()

    #------私有成员------
    def _read_bin(self, filepath:str) -> BinData:
        """读取 .bin 文件头和BinData"""
        with open(filepath, 'rb') as fid:
            # 省略前面相同的 header 读取
            dev_code = np.fromfile(fid, np.int32, 1)
            channel_code = np.fromfile(fid, np.int32, 1)
            data_code = np.fromfile(fid, np.uint8, 16)
            tv_sec = np.fromfile(fid, np.int32, 1)
            tv_usec = np.fromfile(fid, np.int32, 1)
            refractive_index = np.fromfile(fid, np.float32, 1)
            space_resolution = np.fromfile(fid, np.float32, 1)
            frame_freq_hz    = np.fromfile(fid, np.float32, 1)[0]
            sample_interval  = np.fromfile(fid, np.float32, 1)[0]
            sample_data_num  = np.fromfile(fid, np.int32,   1)[0]
            pos_index_from_origin = np.fromfile(fid, dtype=np.int32, count=1)[0]
            space_point_num_per_frame = np.fromfile(fid, dtype=np.int32, count=1)[0]
            store_frame_num = np.fromfile(fid, dtype=np.int32, count=1)[0]
            data_length = np.fromfile(fid, dtype=np.int32, count=1)[0]
            process_frame_num = np.fromfile(fid, dtype=np.int32, count=1)[0]
            cable_code = np.fromfile(fid, dtype=np.int32, count=1)[0]
            
            # 新增字段
            data_flag01 = np.fromfile(fid, dtype=np.uint32, count=1)[0]
            res_dumparr = np.fromfile(fid, dtype=np.uint8, count=104)  
            background_erg = np.fromfile(fid, dtype=np.float64, count=1)[0]
            data_short = np.fromfile(fid, np.int16, count=sample_data_num)

        return BinData(dev_code, channel_code, data_code, tv_sec, tv_usec, refractive_index, space_resolution, frame_freq_hz, 
                       sample_interval, sample_data_num, pos_index_from_origin, space_point_num_per_frame, store_frame_num, 
                       data_length, process_frame_num, cable_code, data_flag01, res_dumparr, background_erg, data_short)

    def _design_filter(self, fs: float, fp: float = 5.0, 
                       fsb: float = 1.0, rp: float = 2.0, rs: float = 50.0) -> Tuple[np.ndarray,np.ndarray]:
        """设计高通巴特沃斯滤波器"""
        Wp = fp/(fs/2); Ws = fsb/(fs/2)
        n, Wn = buttord(Wp, Ws, rp, rs)
        B,A = butter(n, Wn, btype='high')
        return B,A

    @abstractmethod
    def _compute(self, bin_data: BinData):
        """子类实现：对 BinData 做处理并返回绘图所需数据结构"""
        pass

    @abstractmethod
    def _plot(self, result, idx: int, filename: str):
        """子类实现：根据 compute 的结果绘图并保存"""
        pass

    def _post_run(self):
        """可选钩子：在所有文件处理完后执行,
        例如SpectrumProcessor没有重构就会pass，
        EnergyProcessor有实例就会执行子类函数"""
        pass

#---专有类：绘制频谱瀑布图---
class SpectrumProcessor(BaseProcessor):
    # 重构初始化？
    def __init__(self, input_dir:str, output_dir:str, max_freq:float=60.0, view_mode:str="side", dpi = 300):
        super().__init__(input_dir, output_dir, dpi)
        self.max_freq = max_freq
        self.view_mode = view_mode.lower()

    #------私有成员------
    def _compute(self, bin_data: BinData) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # 差分积分 + 高通滤波
        data = bin_data.data
        b, a = self._design_filter(bin_data.frame_freq_hz)
        filtered = np.array([lfilter(b, a, np.cumsum(row)) for row in data])
        amplitude = filtered.T

        # 取第一块
        block_len = min(8192, amplitude.shape[0])
        amp_block = amplitude[:block_len, :]

        N = amp_block.shape[0]
        window = windows.boxcar(N)
        Pxx = np.zeros((N, amp_block.shape[1]))
        for i in range(amp_block.shape[1]):
            f, spec = welch(
                amp_block[:,i], fs=bin_data.frame_freq_hz,
                window=window, nperseg=N, noverlap=0,
                nfft=N, return_onesided=False, scaling='density'
            )
            Pxx[:,i] = spec/bin_data.frame_freq_hz
        # 截断，避免产生inf和nan计算警告
        min_power_threshold = 2e-9 #手动调出来类似于matlab处理的效果。
        Pxx_masked = np.where(Pxx <= min_power_threshold, min_power_threshold, Pxx)
        Pxx_db = 10 * np.log10(Pxx_masked)        
        # 频率轴
        f2 = fftshift(f) + bin_data.frame_freq_hz/2
        loc = np.linspace(0, amp_block.shape[1]-1, amp_block.shape[1])*bin_data.sample_interval
        return loc, f2, Pxx_db

    def _plot(self, result: Tuple[np.ndarray, np.ndarray, np.ndarray], idx:int, filename:str) -> None:
        #--绘图--
        loc, f2, Pxx_db = result
        mask = (f2>0)&(f2<=self.max_freq)
        X, Y = np.meshgrid(loc, f2[mask])
        Z = Pxx_db[mask,:]

        fig = plt.figure(idx, figsize=(8,6), dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(
            X, Y, Z, cmap='viridis', linewidth=0, antialiased=False,
            rcount=256, ccount=128
        )
        ax.set_ylim(0, self.max_freq)
        ax.set_xlabel('x-位置'); ax.set_ylabel('频率(Hz)'); ax.set_zlabel('功率(dB)')
        ax.set_title(f'{filename} 谱瀑布图')
        if self.view_mode=='top': ax.view_init(90,270)
        surf.norm.vmin, surf.norm.vmax = Z.min(), Z.max()
        fig.colorbar(surf, ax=ax, extend='both', extendrect=True)
        out = os.path.splitext(filename)[0] + ('_top' if self.view_mode=='top' else '_side') + '.png'
        plt.savefig(os.path.join(self.output_dir,out), dpi=self.dpi)
        plt.close(fig)  

    #---公有成员：重构run---
    def run(self) -> None:
        print("SpectrumWaterFall mask begin...")
        super().run()


#---专有类：绘制能量瀑布图---
class EnergyProcessor(BaseProcessor):
    def __init__(self, input_dir:str, output_dir:str, dpi:int=300, block_len:int=1024) -> None:
        super().__init__(input_dir, output_dir, dpi)
        self.block_len = block_len
        self._acc = []  # 用于累积 RMS 块
    #------私有成员------
    def _compute(self, bin_data: BinData) -> Tuple[np.ndarray, np.ndarray, float]:
        data = bin_data.data
        b, a = self._design_filter(bin_data.frame_freq_hz)
        filtered = np.array([lfilter(b, a, np.cumsum(row)) for row in data]).T

        # 分块 RMS
        r, c = filtered.shape
        m = r//self.block_len
        rms = np.zeros((m,c))
        # for blk in range(m):
        #     chunk = filtered[blk*self.block_len:(blk+1)*self.block_len]
        #     # 滑动对累加 + 开方
        #     for col in range(c):
        #         s = 0.0
        #         for k in range(chunk.shape[0]-1):
        #             s += chunk[k,col]**2 + chunk[k+1,col]**2
        #         rms[blk,col] = np.sqrt(s / chunk.shape[0])
        # 优化计算逻辑，运行时间有明显降低
        for i in range(m):
            chunk = filtered[i*self.block_len:(i+1)*self.block_len]
            rms[i] = np.sqrt(np.mean(chunk**2, axis=0))

        # 累积全局
        self._acc.append(rms)
        return (rms, bin_data.sample_interval, bin_data.frame_freq_hz)

    def _plot(self, result:Tuple[np.ndarray, np.ndarray, float], idx:int, filename:str) -> None:
        rms, si, fs = result
        m, c = rms.shape
        loc = np.linspace(0, c-1, c)*si
        t   = np.arange(1,m+1)*(self.block_len/fs)
        X, Y = np.meshgrid(loc, t)

        fig = plt.figure(idx, figsize=(10,6), dpi=self.dpi)
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, rms, cmap='viridis', linewidth=0, 
                               antialiased=False, shade=True,rcount=X.shape[0], ccount=X.shape[1])
        ax.view_init(90,270)
        ax.set_xlabel('x-位置'); ax.set_ylabel('时间'); ax.set_zlabel('RMS')
        ax.set_title(f'{filename} 能量瀑布图')
        fig.colorbar(surf, extend='both', extendrect=True)
        out = os.path.splitext(filename)[0] + '_energy.png'
        plt.savefig(os.path.join(self.output_dir,out), dpi=self.dpi)
        plt.close(fig)

    def _post_run(self) -> None:
        # 汇总RMS绘图
        all_rms = np.vstack(self._acc)
        m,c = all_rms.shape
        loc = np.linspace(0,c-1,c)
        t   = np.arange(1,m+1)*(self.block_len/self._acc[0].shape[1])
        X, Y = np.meshgrid(loc,t)
        # 3D瀑布图
        fig1 = plt.figure(999, figsize=(10,6), dpi=self.dpi)
        ax1 = fig1.add_subplot(111, projection='3d')
        surf = ax1.plot_surface(X, Y, all_rms, cmap='viridis', linewidth=0)
        ax1.view_init(30,-60)
        ax1.set_title('汇总能量瀑布图')
        fig1.colorbar(surf, ax=ax1, extend='both', extendrect=True)
        plt.savefig(os.path.join(self.output_dir,'summary_energy.png'), dpi=self.dpi)
        plt.close(fig1)
        # 行求和曲线
        row_sum = np.sum(all_rms, axis=0)
        fig2 = plt.figure(101, figsize=(10,6), dpi=self.dpi)
        plt.plot(loc, row_sum)
        plt.xlabel('位置')
        plt.ylabel('RMS 总和')
        plt.title('均方根总和曲线')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'summary_rms_sum.png'), dpi=self.dpi)
        plt.close(fig2)

    #---公有成员：重构run---
    def run(self) -> None:
        print("EnergyWaterFall mask begin...")
        super().run()


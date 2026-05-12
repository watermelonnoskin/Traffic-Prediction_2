import numpy as np
import os

def analyze_city_data(city):
    """分析城市数据文件结构"""
    print(f"\n{'='*60}")
    print(f"分析城市: {city.upper()}")
    print('='*60)
    
    # 数据文件路径
    data_file = f'{city}/data_{city}.npy'
    label_file = f'{city}/label.npy'
    
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        return
    
    # 加载数据
    data = np.load(data_file)
    print(f"\n数据文件: {data_file}")
    print(f"数据形状: {data.shape}")
    print(f"数据类型: {data.dtype}")
    
    # 分析维度
    if len(data.shape) == 3:
        num_timestamps, num_regions, num_features = data.shape
        print(f"\n维度分析:")
        print(f"  - 时间步数: {num_timestamps}")
        print(f"  - 区域数: {num_regions}")
        print(f"  - 特征数: {num_features}")
        
        # 估算时间跨度
        # 通常交通数据是每30分钟或1小时一个时间步
        if num_timestamps > 0:
            print(f"\n时间跨度估算:")
            print(f"  - 如果是每30分钟一个点: 约 {num_timestamps * 0.5:.1f} 小时 = {num_timestamps * 0.5 / 24:.1f} 天")
            print(f"  - 如果是每小时一个点: 约 {num_timestamps:.1f} 小时 = {num_timestamps / 24:.1f} 天")
            
        # 显示前几个时间步的数据样本
        print(f"\n前3个时间步的数据样本 (第一个区域):")
        for i in range(min(3, num_timestamps)):
            print(f"  时间步 {i}: {data[i, 0, :5]}... (显示前5个特征)")
    
    # 分析标签文件
    if os.path.exists(label_file):
        label = np.load(label_file)
        print(f"\n标签文件: {label_file}")
        print(f"标签形状: {label.shape}")
        print(f"标签类型: {label.dtype}")
        if len(label.shape) >= 1:
            print(f"标签样本 (前5个): {label[:5]}")
    
    # 数据统计
    print(f"\n数据统计:")
    print(f"  - 最小值: {np.min(data):.6f}")
    print(f"  - 最大值: {np.max(data):.6f}")
    print(f"  - 平均值: {np.mean(data):.6f}")
    print(f"  - 标准差: {np.std(data):.6f}")

if __name__ == '__main__':
    # 分析两个城市的数据
    for city in ['nyc', 'chicago']:
        analyze_city_data(city)
    
    print("\n" + "="*60)
    print("分析完成")
    print("="*60)

from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据文件路径
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据缓存
DATA_CACHE = {}
LABEL_CACHE = {}

def load_city_data(city):
    """加载城市数据到缓存"""
    if city in DATA_CACHE:
        return DATA_CACHE[city], LABEL_CACHE.get(city)
    
    data_file = os.path.join(DATA_DIR, city, f'data_{city}.npy')
    label_file = os.path.join(DATA_DIR, city, 'label.npy')
    
    if not os.path.exists(data_file):
        return None, None
    
    try:
        data = np.load(data_file)
        label = np.load(label_file) if os.path.exists(label_file) else None
        DATA_CACHE[city] = data
        LABEL_CACHE[city] = label
        print(f"Loaded {city} data: shape={data.shape}")
        return data, label
    except Exception as e:
        print(f"Error loading {city} data: {e}")
        return None, None

def get_data_info(city):
    """获取数据信息"""
    data, label = load_city_data(city)
    if data is None:
        return None
    
    num_timestamps, num_regions, num_features = data.shape
    
    # 假设数据从某个基准日期开始，每小时一个时间点
    # 数据从2016年1月1日开始
    base_date = datetime(2016, 1, 1, 0, 0)
    
    # 计算可用日期范围
    total_hours = num_timestamps
    total_days = total_hours // 24
    
    return {
        'city': city,
        'shape': list(data.shape),
        'num_timestamps': num_timestamps,
        'num_regions': num_regions,
        'num_features': num_features,
        'base_date': base_date.isoformat(),
        'total_days': total_days,
        'available_dates': [
            (base_date + timedelta(days=i)).strftime('%Y-%m-%d') 
            for i in range(min(total_days, 30))  # 只返回前30天
        ]
    }

def get_timestep_for_date(city, date_str, hour=0):
    """根据日期字符串获取时间步索引"""
    data, _ = load_city_data(city)
    if data is None:
        return None
    
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        base_date = datetime(2016, 1, 1, 0, 0)
        
        # 计算从基准日期到目标日期的天数
        days_diff = (target_date - base_date).days
        if days_diff < 0:
            return None
        
        # 计算时间步索引 (每小时一个点)
        timestep = days_diff * 24 + hour
        num_timestamps = data.shape[0]
        
        if timestep >= num_timestamps:
            return None
        
        return timestep
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'API server is running'})

@app.route('/api/data/<city>', methods=['GET'])
def get_traffic_data(city):
    """
    获取指定城市的交通数据
    :param city: 城市名称 (nyc 或 chicago)
    """
    try:
        if city not in ['nyc', 'chicago']:
            return jsonify({'error': 'Invalid city name'}), 400
        
        data_file = os.path.join(DATA_DIR, city, f'data_{city}.npy')
        label_file = os.path.join(DATA_DIR, city, 'label.npy')
        
        if not os.path.exists(data_file):
            return jsonify({'error': f'Data file not found for {city}'}), 404
        
        # 加载数据
        data = np.load(data_file)
        label = np.load(label_file) if os.path.exists(label_file) else None
        
        # 将numpy数组转换为可序列化的格式
        data_list = data.tolist() if data is not None else None
        label_list = label.tolist() if label is not None else None
        
        return jsonify({
            'city': city,
            'data_shape': list(data.shape) if data is not None else None,
            'data': data_list,
            'label': label_list,
            'data_type': str(data.dtype) if data is not None else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<city>/stats', methods=['GET'])
def get_data_stats(city):
    """
    获取指定城市数据的统计信息
    :param city: 城市名称 (nyc 或 chicago)
    """
    try:
        if city not in ['nyc', 'chicago']:
            return jsonify({'error': 'Invalid city name'}), 400
        
        data_file = os.path.join(DATA_DIR, city, f'data_{city}.npy')
        
        if not os.path.exists(data_file):
            return jsonify({'error': f'Data file not found for {city}'}), 404
        
        data = np.load(data_file)
        
        return jsonify({
            'city': city,
            'shape': list(data.shape),
            'dtype': str(data.dtype),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'median': float(np.median(data))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/performance', methods=['GET'])
def get_model_performance():
    """
    获取模型性能数据
    可以从results目录读取训练结果，或者返回模拟数据
    """
    try:
        # 检查results目录是否存在训练结果
        results_dir = os.path.join(DATA_DIR, 'results')
        
        # 这里可以添加读取真实训练结果的逻辑
        # 目前返回模拟数据，可以根据实际训练结果修改
        model_performance = [
            {'name': 'MyPlan', 'value': 85.3, 'mae': 12.5, 'rmse': 18.2},
            {'name': 'LSTM', 'value': 78.6, 'mae': 15.8, 'rmse': 22.4},
            {'name': 'GRU', 'value': 75.2, 'mae': 16.3, 'rmse': 23.1},
            {'name': 'MLP', 'value': 70.8, 'mae': 18.7, 'rmse': 26.5}
        ]
        
        return jsonify({
            'models': model_performance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic/flow', methods=['GET'])
def get_traffic_flow():
    """
    获取交通流量趋势数据（24小时）
    支持从真实数据文件中提取指定日期的流量趋势
    """
    try:
        city = request.args.get('city', 'nyc')
        date_str = request.args.get('date', None)  # 格式: YYYY-MM-DD
        
        # 尝试从真实数据加载
        data, _ = load_city_data(city)
        
        if data is not None and date_str:
            # 从真实数据提取
            hours = []
            city_flow = []
            
            for hour in range(24):
                timestep = get_timestep_for_date(city, date_str, hour)
                if timestep is not None and timestep < data.shape[0]:
                    # 使用第一个特征作为流量指标（通常是流量）
                    # 对所有区域求和得到城市总流量
                    total_flow = float(np.sum(data[timestep, :, 0]))
                    hours.append(f'{hour}:00')
                    city_flow.append(round(total_flow, 2))
                else:
                    # 超出数据范围，使用模拟数据
                    hours.append(f'{hour}:00')
                    city_flow.append(round(500 + np.random.randint(-100, 400), 2))
            
            return jsonify({
                'hours': hours,
                'city': city,
                'date': date_str,
                'is_real_data': True,
                city: city_flow
            })
        else:
            # 返回模拟数据
            hours = [f'{i}:00' for i in range(24)]
            return jsonify({
                'hours': hours,
                'city': city,
                'date': date_str or 'simulated',
                'is_real_data': False,
                city: [500 + np.random.randint(-100, 400) for _ in range(24)]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic/district', methods=['GET'])
def get_district_data():
    """
    获取各区域流量数据
    支持从真实数据文件中提取指定时间的区域数据
    """
    try:
        city = request.args.get('city', 'nyc')
        date_str = request.args.get('date', None)
        hour = int(request.args.get('hour', 12))
        
        # 区域名称
        district_names = ['区域1', '区域2', '区域3', '区域4', '区域5', 
                         '区域6', '区域7', '区域8', '区域9', '区域10']
        
        data, _ = load_city_data(city)
        
        if data is not None and date_str:
            timestep = get_timestep_for_date(city, date_str, hour)
            if timestep is not None and timestep < data.shape[0]:
                # 从真实数据提取各区域数据
                num_regions = min(data.shape[1], len(district_names))
                district_data = []
                
                for i in range(num_regions):
                    # 使用第一个特征作为流量值
                    current = float(data[timestep, i, 0])
                    # 模拟预测值（在真实值附近波动）
                    predicted = current * (1 + np.random.uniform(-0.1, 0.1))
                    
                    district_data.append({
                        'district': district_names[i],
                        'current': round(current, 2),
                        'predicted': round(predicted, 2)
                    })
                
                return jsonify({
                    'city': city,
                    'date': date_str,
                    'hour': hour,
                    'is_real_data': True,
                    'districts': district_data
                })
        
        # 返回模拟数据
        district_data = []
        for district in district_names[:5]:
            current = np.random.randint(300, 1100)
            predicted = current + np.random.randint(-50, 50)
            district_data.append({
                'district': district,
                'current': int(current),
                'predicted': int(predicted)
            })
        
        return jsonify({
            'city': city,
            'date': date_str or 'simulated',
            'hour': hour,
            'is_real_data': False,
            'districts': district_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic/heatmap', methods=['GET'])
def get_heatmap_data():
    """
    获取热力图数据（一周7天x24小时）
    支持从真实数据文件中提取指定日期范围的热力图数据
    """
    try:
        city = request.args.get('city', 'nyc')
        start_date_str = request.args.get('start_date', None)  # 周一开始的日期
        
        days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        data = []
        
        real_data_loaded = False
        data_array, _ = load_city_data(city)
        
        if data_array is not None and start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                real_data_loaded = True
                
                for day_index in range(7):
                    current_date = start_date + timedelta(days=day_index)
                    date_str = current_date.strftime('%Y-%m-%d')
                    
                    for hour in range(24):
                        timestep = get_timestep_for_date(city, date_str, hour)
                        if timestep is not None and timestep < data_array.shape[0]:
                            # 计算所有区域的平均流量
                            avg_flow = float(np.mean(data_array[timestep, :, 0]))
                            value = int(avg_flow * 100)  # 缩放以便显示
                        else:
                            value = np.random.randint(20, 80)
                        
                        data.append([hour, day_index, value])
            except Exception as e:
                print(f"Error loading real heatmap data: {e}")
                real_data_loaded = False
        
        if not real_data_loaded:
            # 生成模拟数据
            for day_index, day in enumerate(days):
                is_weekend = day_index >= 5
                for hour in range(24):
                    base_value = 30 if is_weekend else 50
                    
                    if not is_weekend and ((hour >= 7 and hour <= 9) or (hour >= 17 and hour <= 19)):
                        base_value = 85 + np.random.random() * 15
                    elif not is_weekend and (hour >= 12 and hour <= 13):
                        base_value = 70 + np.random.random() * 10
                    elif hour >= 0 and hour <= 5:
                        base_value = 5 + np.random.random() * 10
                    else:
                        base_value = 40 + np.random.random() * 30
                    
                    data.append([hour, day_index, int(base_value)])
        
        return jsonify({
            'city': city,
            'start_date': start_date_str or 'simulated',
            'is_real_data': real_data_loaded,
            'data': data,
            'days': days
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/scatter', methods=['GET'])
def get_scatter_data():
    """
    获取预测vs实际散点图数据
    支持从真实标签数据和模型预测结果中提取
    """
    try:
        city = request.args.get('city', 'nyc')
        data = []
        
        # 尝试从真实数据生成散点图
        _, label = load_city_data(city)
        
        if label is not None:
            # 标签是二维数组 (timestamps, regions)
            # 随机采样时间和区域
            num_timestamps, num_regions = label.shape
            sample_size = min(100, num_timestamps * num_regions)
            
            for _ in range(sample_size):
                t_idx = np.random.randint(0, num_timestamps)
                r_idx = np.random.randint(0, num_regions)
                actual = float(label[t_idx, r_idx])
                # 模拟预测值：在实际值基础上添加误差
                noise = np.random.normal(0, max(actual * 0.1, 0.1))  # 10%的误差，最小0.1
                predicted = actual + noise
                data.append([round(actual, 2), round(predicted, 2)])
        else:
            # 生成模拟数据
            for _ in range(100):
                actual = np.random.random() * 1000
                predicted = actual + (np.random.random() - 0.5) * 200
                data.append([round(float(actual), 2), round(float(predicted), 2)])
        
        return jsonify({
            'city': city,
            'is_real_data': label is not None,
            'data': data
        })
    except Exception as e:
        import traceback
        print(f"Error in scatter API: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/info/<city>', methods=['GET'])
def get_data_info_api(city):
    """
    获取数据信息（可用日期范围等）
    """
    try:
        if city not in ['nyc', 'chicago']:
            return jsonify({'error': 'Invalid city name'}), 400
        
        info = get_data_info(city)
        if info is None:
            return jsonify({'error': f'Failed to load data for {city}'}), 404
        
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Traffic API Server...")
    print("API will be available at: http://localhost:5000")
    
    # 预加载数据
    print("Pre-loading data...")
    for city in ['nyc', 'chicago']:
        load_city_data(city)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

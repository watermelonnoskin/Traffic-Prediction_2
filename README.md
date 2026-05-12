# 交通数据可视化系统

基于 Vue.js + Flask 的交通流量预测与可视化平台，支持 NYC 和 Chicago 两个城市的交通数据分析。

## 项目结构

```
trafficcompare2/
├── src/                          # 前端源代码
│   ├── components/               # Vue 组件
│   │   └── TrafficDashboard.vue  # 主仪表盘组件
│   ├── App.vue                   # 根组件
│   └── main.js                   # 入口文件
├── nyc/                          # NYC 数据集
│   ├── data_nyc.npy              # 特征数据 (13128, 64, 116)
│   └── label.npy                 # 标签数据 (13128, 64)
├── chicago/                      # Chicago 数据集
│   ├── data_chicago.npy          # 特征数据 (8784, 27, 116)
│   └── label.npy                 # 标签数据 (8784, 27)
├── api_server.py                 # Flask 后端 API
├── train.py                      # 模型训练脚本
├── test.py                       # 数据查看工具
├── analyze_data.py               # 数据分析工具
├── index.html                    # 前端入口
├── package.json                  # Node.js 依赖
├── requirement.txt               # Python 依赖
└── vite.config.js                # Vite 配置
```

## 技术栈

### 前端
- **Vue 3** - 框架
- **ECharts** - 图表库
- **Vite** - 构建工具

### 后端
- **Flask** - Web 框架
- **Flask-CORS** - 跨域支持
- **NumPy** - 数据处理

### 模型训练
- **TensorFlow 2.10.0**
- **Python 3.9**

## 快速启动

### 1. 环境准备

创建 Python 虚拟环境（推荐）：

```bash
# 使用 conda
conda create -n traffic_api python=3.9
conda activate traffic_api

# 或使用 venv
python -m venv traffic_api
source traffic_api/bin/activate  # Linux/Mac
traffic_api\Scripts\activate      # Windows
```

### 2. 安装依赖

**后端依赖：**
```bash
pip install -r requirement.txt
```

**前端依赖：**
```bash
npm install
```

### 3. 启动后端 API

```bash
python api_server.py
```

后端服务将在 `http://localhost:5000` 启动，输出示例：
```
Starting Traffic API Server...
API will be available at: http://localhost:5000
Pre-loading data...
Loaded nyc data: shape=(13128, 64, 116)
Loaded chicago data: shape=(8784, 27, 116)
 * Running on http://127.0.0.1:5000
```

### 4. 启动前端

```bash
npm run dev
```

前端开发服务器将在 `http://localhost:5173` 启动（Vite 默认端口）。

### 5. 访问应用

打开浏览器访问：`http://localhost:5173`

## API 接口

后端提供以下 RESTful API：

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/data/info/<city>` | GET | 获取数据信息（日期范围等） |
| `/api/data/<city>` | GET | 获取原始数据 |
| `/api/data/<city>/stats` | GET | 获取数据统计信息 |
| `/api/traffic/flow` | GET | 获取24小时流量趋势 |
| `/api/traffic/district` | GET | 获取各区域流量数据 |
| `/api/traffic/heatmap` | GET | 获取一周热力图数据 |
| `/api/model/performance` | GET | 获取模型性能数据 |
| `/api/prediction/scatter` | GET | 获取预测vs实际散点图数据 |

### 查询参数

- `city`: 城市名称 (`nyc` 或 `chicago`)
- `date`: 日期格式 `YYYY-MM-DD` (如 `2016-01-01`)
- `hour`: 小时 (0-23)
- `start_date`: 热力图起始日期（周一开始）

## 数据说明

### 数据时间范围

- **基准日期**: 2016-01-01
- **NYC**: 约 547 天（每小时一个点）
- **Chicago**: 约 366 天（每小时一个点）

### 数据结构

- **特征数据**: `(时间步数, 区域数, 特征数)`
  - NYC: `(13128, 64, 116)`
  - Chicago: `(8784, 27, 116)`
- **标签数据**: `(时间步数, 区域数)`

## 训练模型

### MyPlan 模型（主模型）

```bash
# NYC
python train.py --gpus 0 --dataset nyc --model myplan --evolution_smooth 1 --streaming_postprocess 1

# Chicago
python train.py --gpus 0 --dataset chicago --model myplan --evolution_smooth 1 --streaming_postprocess 1
```

### 基线模型

```bash
# LSTM
python train.py --gpus 0 --dataset nyc --model lstm

# GRU
python train.py --gpus 0 --dataset nyc --model gru

# MLP
python train.py --gpus 0 --dataset nyc --model mlp
```

## 数据查看工具

```bash
# 查看数据文件信息
python test.py nyc/data_nyc.npy --stats

# 查看前20个元素
python test.py nyc/data_nyc.npy --max_print 20

# 数据分析
python analyze_data.py
```

## 配置说明

### 后端配置 (`api_server.py`)

```python
# 数据基准日期（根据实际数据修改）
base_date = datetime(2016, 1, 1, 0, 0)

# API 端口
app.run(host='0.0.0.0', port=5000, debug=True)
```

### 前端配置 (`src/components/TrafficDashboard.vue`)

```javascript
// API 地址
apiUrl: 'http://localhost:5000/api'

// 默认选择
defaultCity: 'nyc'
defaultDate: '2016-01-01'
```

## 常见问题

### 1. 前端无法连接后端

确保后端服务已启动，且前端 `apiUrl` 配置正确。

### 2. CORS 跨域错误

后端已配置 `flask-cors`，如仍有问题请检查浏览器安全设置。

### 3. 数据日期不正确

修改 `api_server.py` 中的 `base_date` 为实际数据起始日期。

## Requirements

- Python 3.9
- TensorFlow 2.10.0
- 或 TensorFlow-GPU 2.10.0（需要 CUDA 11.2 + cuDNN 8.1）
- Node.js 16+
- 其他依赖见 `requirement.txt` 和 `package.json`

## License

MIT

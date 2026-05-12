<template>
  <div class="traffic-dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <h1>🚗 交通数据可视化系统</h1>
        <span class="subtitle">Traffic Data Visualization</span>
      </div>
      <div class="controls">
        <div class="control-group">
          <label>城市</label>
          <select v-model="selectedCity" @change="onCityChange" class="control-select">
            <option value="nyc">🗽 纽约</option>
            <option value="chicago">🏙️ 芝加哥</option>
          </select>
        </div>
        <div class="control-group">
          <label>模型</label>
          <select v-model="selectedModel" @change="updateData" class="control-select">
            <option value="myplan">🎯 MyPlan</option>
            <option value="lstm">🧠 LSTM</option>
            <option value="gru">⚡ GRU</option>
            <option value="mlp">🔧 MLP</option>
          </select>
        </div>
        <div class="control-group">
          <label>粒度</label>
          <select v-model="selectedGranularity" @change="updateData" class="control-select">
            <option value="1h">⏰ 1小时</option>
            <option value="30min">⏱️ 30分钟</option>
            <option value="15min">⚡ 15分钟</option>
          </select>
        </div>
        <div class="control-group">
          <label>日期</label>
          <input 
            type="date" 
            v-model="selectedDate" 
            @change="updateData"
            :min="minDate"
            :max="maxDate"
            class="date-picker"
          />
        </div>
        <div class="control-group">
          <label>路段</label>
          <select v-model="selectedRoadId" @change="updateData" class="control-select">
            <option value="">全部路段</option>
            <option v-for="road in availableRoads" :key="road.id" :value="road.id">
              {{ road.name }}
            </option>
          </select>
        </div>
        <div v-if="loading" class="loading-indicator">
          <span class="spinner"></span>
          加载中...
        </div>
        <button 
          v-else 
          class="data-toggle-btn" 
          @click="toggleDataSource"
          :class="{ 'real': dataInfo.isRealData, 'simulated': !dataInfo.isRealData }"
        >
          <span class="badge-icon">{{ dataInfo.isRealData ? '✓' : '~' }}</span>
          {{ dataInfo.isRealData ? '真实数据' : '模拟数据' }}
        </button>
      </div>
    </header>

    <!-- 数据概览卡片 -->
    <section class="stats-overview" v-if="trafficData.flowData">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ getTotalFlow() }}</div>
          <div class="stat-label">总流量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ getPeakHour() }}</div>
          <div class="stat-label">高峰时段</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏘️</div>
        <div class="stat-content">
          <div class="stat-value">{{ trafficData.districts?.length || 0 }}</div>
          <div class="stat-label">区域数量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-value">{{ getAccuracy() }}%</div>
          <div class="stat-label">预测准确率</div>
        </div>
      </div>
    </section>

    <main class="dashboard-content">
      <div class="chart-grid">
        <!-- 交通流量趋势图 -->
        <div class="chart-container">
          <div class="chart-header">
            <h3>📈 交通流量趋势</h3>
            <span class="chart-subtitle">{{ getGranularityLabel() }}流量变化</span>
          </div>
          <v-chart :option="lineChartOption" class="chart-body" />
        </div>

        <!-- 模型性能对比 -->
        <div class="chart-container">
          <div class="chart-header">
            <h3>🏆 模型性能对比</h3>
            <span class="chart-subtitle">各模型准确率对比</span>
          </div>
          <v-chart :option="pieChartOption" class="chart-body" />
        </div>

        <!-- 热力图 -->
        <div class="chart-container full-width">
          <div class="chart-header">
            <h3>🔥 交通流量热力图</h3>
            <span class="chart-subtitle">一周7天×24小时流量分布</span>
          </div>
          <v-chart :option="heatmapOption" class="chart-body heatmap-body" />
        </div>

        <!-- 预测vs实际 -->
        <div class="chart-container full-width">
          <div class="chart-header">
            <h3>🎯 预测 vs 实际</h3>
            <span class="chart-subtitle">预测准确性分析</span>
          </div>
          <v-chart :option="scatterChartOption" class="chart-body" />
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'TrafficDashboard',
  data() {
    return {
      selectedCity: 'nyc',
      selectedModel: 'myplan',
      selectedGranularity: '1h',  // 默认1小时粒度
      selectedRoadId: '',  // 默认全部路段
      selectedDate: '2016-01-01',  // 默认日期
      minDate: '2016-01-01',
      maxDate: '2016-01-31',
      availableDates: [],
      availableRoads: [],  // 可用路段列表
      trafficData: [],
      lineChartOption: {},
      barChartOption: {},
      heatmapOption: {},
      pieChartOption: {},
      scatterChartOption: {},
      apiUrl: 'http://localhost:5000/api',
      loading: false,
      dataInfo: {
        isRealData: false,
        date: null
      }
    }
  },
  mounted() {
    this.updateAvailableRoads()
    this.fetchDataInfo()
  },
  methods: {
    generateMockData() {
      // 生成模拟交通数据
      const hours = Array.from({length: 24}, (_, i) => `${i}:00`)
      const districts = ['曼哈顿', '布鲁克林', '皇后区', '布朗克斯', '史泰登岛']
      
      // 生成更真实的流量趋势数据
      this.trafficData = {
        hours,
        districts,
        flowData: hours.map((hour, index) => {
          // 模拟早晚高峰模式
          const hourNum = index
          let baseFlowNYC = 500
          let baseFlowChicago = 400
          
          // 早晚高峰（7-9点，17-19点）
          if ((hourNum >= 7 && hourNum <= 9) || (hourNum >= 17 && hourNum <= 19)) {
            baseFlowNYC = 1200 + Math.random() * 300
            baseFlowChicago = 900 + Math.random() * 200
          }
          // 午高峰（12-13点）
          else if (hourNum >= 12 && hourNum <= 13) {
            baseFlowNYC = 900 + Math.random() * 200
            baseFlowChicago = 700 + Math.random() * 150
          }
          // 深夜低流量
          else if (hourNum >= 0 && hourNum <= 5) {
            baseFlowNYC = 200 + Math.random() * 100
            baseFlowChicago = 150 + Math.random() * 80
          }
          // 其他时间
          else {
            baseFlowNYC = 600 + Math.random() * 200
            baseFlowChicago = 450 + Math.random() * 150
          }
          
          return {
            hour,
            nyc: Math.floor(baseFlowNYC),
            chicago: Math.floor(baseFlowChicago)
          }
        }),
        districtData: districts.map(district => {
          const current = Math.floor(Math.random() * 800) + 300
          // 预测值在当前值附近波动
          const predicted = current + Math.floor((Math.random() - 0.5) * 100)
          return {
            district,
            current,
            predicted
          }
        }),
        heatmapData: this.generateHeatmapData(),
        modelPerformance: [
          { name: 'MyPlan', value: 85.3 },
          { name: 'LSTM', value: 78.6 },
          { name: 'GRU', value: 75.2 },
          { name: 'MLP', value: 70.8 }
        ],
        predictionData: this.generateScatterData()
      }
    },

    generateHeatmapData() {
      const data = []
      const hours = Array.from({length: 24}, (_, i) => i)
      const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      
      // 模拟更真实的交通流量模式
      // 工作日早晚高峰流量高，周末流量较低且分布均匀
      days.forEach((day, dayIndex) => {
        const isWeekend = dayIndex >= 5 // 周六、周日
        hours.forEach(hour => {
          let baseValue = isWeekend ? 30 : 50
          
          // 工作日早晚高峰（7-9点，17-19点）
          if (!isWeekend && ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19))) {
            baseValue = 85 + Math.random() * 15
          }
          // 工作日午高峰（12-13点）
          else if (!isWeekend && (hour >= 12 && hour <= 13)) {
            baseValue = 70 + Math.random() * 10
          }
          // 深夜流量低
          else if (hour >= 0 && hour <= 5) {
            baseValue = 5 + Math.random() * 10
          }
          // 其他时间
          else {
            baseValue = 40 + Math.random() * 30
          }
          
          data.push([hour, dayIndex, Math.floor(baseValue)])
        })
      })
      
      return data
    },

    generateScatterData() {
      const data = []
      for (let i = 0; i < 100; i++) {
        const actual = Math.random() * 1000
        const predicted = actual + (Math.random() - 0.5) * 200
        data.push([actual, predicted])
      }
      return data
    },

    initCharts() {
      this.initLineChart()
      this.initBarChart()
      this.initHeatmap()
      this.initPieChart()
      this.initScatterChart()
    },

    initLineChart() {
      this.lineChartOption = {
        title: {
          text: '24小时交通流量趋势',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#ccc',
          borderWidth: 1,
          textStyle: {
            color: '#333'
          },
          formatter: function(params) {
            let result = params[0].name + '<br/>'
            params.forEach(param => {
              result += `${param.marker} ${param.seriesName}: ${param.value}<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['纽约', '芝加哥'],
          top: 40,
          textStyle: {
            fontSize: 14
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.trafficData.hours,
          boundaryGap: false,
          axisLabel: {
            rotate: 45,
            fontSize: 11
          }
        },
        yAxis: {
          type: 'value',
          name: '流量',
          nameTextStyle: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          axisLabel: {
            fontSize: 12
          }
        },
        series: [
          {
            name: '纽约',
            type: 'line',
            data: this.trafficData.flowData.map(item => item.nyc),
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              width: 3,
              color: '#5470c6'
            },
            itemStyle: { color: '#5470c6' },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0,
                  color: 'rgba(84, 112, 198, 0.3)'
                }, {
                  offset: 1,
                  color: 'rgba(84, 112, 198, 0.05)'
                }]
              }
            }
          },
          {
            name: '芝加哥',
            type: 'line',
            data: this.trafficData.flowData.map(item => item.chicago),
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              width: 3,
              color: '#91cc75'
            },
            itemStyle: { color: '#91cc75' },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0,
                  color: 'rgba(145, 204, 117, 0.3)'
                }, {
                  offset: 1,
                  color: 'rgba(145, 204, 117, 0.05)'
                }]
              }
            }
          }
        ]
      }
    },

    initBarChart() {
      this.barChartOption = {
        title: {
          text: '各区域当前 vs 预测流量',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#ccc',
          borderWidth: 1,
          formatter: function(params) {
            let result = params[0].name + '<br/>'
            params.forEach(param => {
              result += `${param.marker} ${param.seriesName}: ${param.value}<br/>`
            })
            // 计算误差
            const current = params[0].value
            const predicted = params[1].value
            const error = Math.abs(predicted - current)
            const errorRate = ((error / current) * 100).toFixed(2)
            result += `<br/>误差: ${error} (${errorRate}%)`
            return result
          }
        },
        legend: {
          data: ['当前流量', '预测流量'],
          top: 40,
          textStyle: {
            fontSize: 14
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.trafficData.districts,
          axisLabel: {
            fontSize: 12,
            interval: 0
          }
        },
        yAxis: {
          type: 'value',
          name: '流量',
          nameTextStyle: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          axisLabel: {
            fontSize: 12
          }
        },
        series: [
          {
            name: '当前流量',
            type: 'bar',
            data: this.trafficData.districtData.map(item => item.current),
            barWidth: '35%',
            itemStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0,
                  color: '#5470c6'
                }, {
                  offset: 1,
                  color: '#91cc75'
                }]
              },
              borderRadius: [4, 4, 0, 0]
            },
            emphasis: {
              itemStyle: {
                color: '#4575b4'
              }
            }
          },
          {
            name: '预测流量',
            type: 'bar',
            data: this.trafficData.districtData.map(item => item.predicted),
            barWidth: '35%',
            itemStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [{
                  offset: 0,
                  color: '#fac858'
                }, {
                  offset: 1,
                  color: '#ee6666'
                }]
              },
              borderRadius: [4, 4, 0, 0]
            },
            emphasis: {
              itemStyle: {
                color: '#d73027'
              }
            }
          }
        ]
      }
    },

    initHeatmap() {
      const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      this.heatmapOption = {
        title: {
          text: '一周交通流量热力图',
          left: 'center',
          textStyle: {
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          position: 'top',
          formatter: function (params) {
            const dayName = days[params.data[1]]
            return `${dayName} ${params.data[0]}:00<br/>流量: ${params.data[2]}`
          }
        },
        grid: {
          height: '70%',
          top: '15%',
          bottom: '20%'
        },
        xAxis: {
          type: 'category',
          data: Array.from({length: 24}, (_, i) => i),
          splitArea: {
            show: true
          },
          axisLabel: {
            rotate: 45,
            formatter: '{value}:00'
          }
        },
        yAxis: {
          type: 'category',
          data: days,
          splitArea: {
            show: true
          }
        },
        visualMap: {
          min: 0,
          max: 100,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '5%',
          textStyle: {
            color: '#333'
          },
          inRange: {
            color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695', '#f46d43', '#d73027', '#a50026']
          }
        },
        series: [{
          name: '流量',
          type: 'heatmap',
          data: this.trafficData.heatmapData,
          label: {
            show: true,
            fontSize: 10,
            color: '#333'
          },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 1
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
              borderColor: '#333',
              borderWidth: 2
            }
          }
        }]
      }
    },

    initPieChart() {
      const sortedData = [...this.trafficData.modelPerformance].sort((a, b) => b.value - a.value)
      this.pieChartOption = {
        title: {
          text: '模型准确率对比',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#ccc',
          borderWidth: 1,
          formatter: function(params) {
            const param = params[0]
            return `${param.name}<br/>准确率: ${param.value}%<br/>排名: 第${param.dataIndex + 1}位`
          }
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '20%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: sortedData.map(item => item.name),
          axisLabel: {
            fontSize: 13,
            interval: 0
          }
        },
        yAxis: {
          type: 'value',
          name: '准确率 (%)',
          nameTextStyle: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        series: [
          {
            name: '准确率',
            type: 'bar',
            data: sortedData.map(item => item.value),
            barWidth: '50%',
            itemStyle: {
              borderRadius: [8, 8, 0, 0],
              color: function(params) {
                const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666']
                return colors[params.dataIndex % colors.length]
              }
            },
            label: {
              show: true,
              position: 'top',
              fontSize: 14,
              fontWeight: 'bold',
              formatter: '{c}%'
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.3)',
                borderWidth: 2,
                borderColor: '#333'
              }
            },
            animationDelay: function(idx) {
              return idx * 100
            }
          }
        ]
      }
    },

    initScatterChart() {
      this.scatterChartOption = {
        title: {
          text: '预测值 vs 实际值',
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#ccc',
          borderWidth: 1,
          formatter: function (params) {
            if (params.seriesName === '完美预测线') {
              return '完美预测线'
            }
            const actual = params.data[0]
            const predicted = params.data[1]
            const error = Math.abs(predicted - actual)
            const errorRate = ((error / actual) * 100).toFixed(2)
            return `实际值: ${actual.toFixed(2)}<br/>预测值: ${predicted.toFixed(2)}<br/>误差: ${error.toFixed(2)} (${errorRate}%)`
          }
        },
        grid: {
          left: '8%',
          right: '8%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '实际值',
          nameTextStyle: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#ccc'
            }
          },
          scale: true
        },
        yAxis: {
          type: 'value',
          name: '预测值',
          nameTextStyle: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#ccc'
            }
          },
          scale: true
        },
        series: [{
          name: '数据点',
          type: 'scatter',
          data: this.trafficData.predictionData,
          symbolSize: function(data) {
            // 根据误差大小调整点的大小
            const error = Math.abs(data[1] - data[0])
            return Math.max(5, Math.min(15, 5 + error / 50))
          },
          itemStyle: {
            color: function(params) {
              // 根据误差大小调整颜色
              const error = Math.abs(params.data[1] - params.data[0])
              const errorRate = error / params.data[0]
              if (errorRate < 0.1) return '#91cc75' // 绿色：误差小
              if (errorRate < 0.2) return '#fac858' // 黄色：误差中等
              return '#ee6666' // 红色：误差大
            },
            opacity: 0.7
          }
        }, {
          name: '完美预测线',
          type: 'line',
          data: [[0, 0], [1200, 1200]],
          lineStyle: {
            color: '#ff0000',
            type: 'dashed',
            width: 2
          },
          showSymbol: false,
          z: 10
        }]
      }
    },

    async onCityChange() {
      // 城市改变时重新获取数据信息
      await this.fetchDataInfo()
      // 更新可用路段列表
      this.updateAvailableRoads()
      await this.fetchDataFromAPI()
    },

    updateAvailableRoads() {
      // 根据城市生成路段列表
      const numRoads = this.selectedCity === 'nyc' ? 64 : 27
      this.availableRoads = Array.from({ length: numRoads }, (_, i) => ({
        id: i + 1,
        name: `路段${i + 1}`
      }))
      // 重置路段选择
      this.selectedRoadId = ''
    },

    getGranularityLabel() {
      const labels = {
        '1h': '24小时',
        '30min': '48点（30分钟）',
        '15min': '96点（15分钟）'
      }
      return labels[this.selectedGranularity] || '24小时'
    },

    toggleDataSource() {
      // 切换数据源
      this.dataInfo.isRealData = !this.dataInfo.isRealData
      if (this.dataInfo.isRealData) {
        this.fetchDataFromAPI()
      } else {
        this.generateMockData()
        this.initCharts()
      }
    },

    async updateData() {
      // 从API重新获取数据
      await this.fetchDataFromAPI()
    },

    async fetchDataInfo() {
      try {
        const response = await fetch(`${this.apiUrl}/data/info/${this.selectedCity}`)
        if (response.ok) {
          const info = await response.json()
          if (info.available_dates && info.available_dates.length > 0) {
            this.minDate = info.available_dates[0]
            this.maxDate = info.available_dates[info.available_dates.length - 1]
            this.availableDates = info.available_dates
            // 如果当前日期不在可用范围内，设置为第一个可用日期
            if (!this.availableDates.includes(this.selectedDate)) {
              this.selectedDate = this.minDate
            }
          }
        }
      } catch (error) {
        console.error('Error fetching data info:', error)
      }
    },

    async fetchDataFromAPI() {
      this.loading = true
      try {
        // 并行获取所有数据
        const [flowData, districtData, heatmapData, modelPerformance, scatterData] = await Promise.all([
          this.fetchTrafficFlow(),
          this.fetchDistrictData(),
          this.fetchHeatmapData(),
          this.fetchModelPerformance(),
          this.fetchScatterData()
        ])

        // 更新数据信息
        this.dataInfo = {
          isRealData: flowData.is_real_data || districtData.is_real_data || heatmapData.is_real_data,
          date: this.selectedDate
        }

        this.trafficData = {
          hours: flowData.hours,
          districts: districtData.districts.map(d => d.district),
          flowData: flowData.hours.map((hour, index) => ({
            hour,
            nyc: this.selectedCity === 'nyc' ? flowData[this.selectedCity][index] : flowData.nyc[index],
            chicago: this.selectedCity === 'chicago' ? flowData[this.selectedCity][index] : flowData.chicago[index]
          })),
          districtData: districtData.districts,
          heatmapData: heatmapData.data,
          modelPerformance: modelPerformance.models,
          predictionData: scatterData.data
        }

        this.initCharts()
      } catch (error) {
        console.error('Error fetching data from API:', error)
        // 如果API失败，回退到模拟数据
        console.log('Falling back to mock data')
        this.dataInfo = { isRealData: false, date: null }
        this.generateMockData()
        this.initCharts()
      } finally {
        this.loading = false
      }
    },

    async fetchTrafficFlow() {
      const response = await fetch(`${this.apiUrl}/traffic/flow?city=${this.selectedCity}&date=${this.selectedDate}&granularity=${this.selectedGranularity}`)
      if (!response.ok) throw new Error('Failed to fetch traffic flow data')
      return await response.json()
    },

    async fetchDistrictData() {
      const roadParam = this.selectedRoadId ? `&road_id=${this.selectedRoadId}` : ''
      const response = await fetch(`${this.apiUrl}/traffic/district?city=${this.selectedCity}&date=${this.selectedDate}&hour=12&granularity=${this.selectedGranularity}${roadParam}`)
      if (!response.ok) throw new Error('Failed to fetch district data')
      return await response.json()
    },

    async fetchHeatmapData() {
      // 计算本周一的日期
      const date = new Date(this.selectedDate)
      const dayOfWeek = date.getDay() // 0是周日，1是周一
      const monday = new Date(date)
      monday.setDate(date.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1))
      const mondayStr = monday.toISOString().split('T')[0]
      
      const response = await fetch(`${this.apiUrl}/traffic/heatmap?city=${this.selectedCity}&start_date=${mondayStr}`)
      if (!response.ok) throw new Error('Failed to fetch heatmap data')
      return await response.json()
    },

    async fetchModelPerformance() {
      const response = await fetch(`${this.apiUrl}/model/performance`)
      if (!response.ok) throw new Error('Failed to fetch model performance')
      return await response.json()
    },

    async fetchScatterData() {
      const response = await fetch(`${this.apiUrl}/prediction/scatter?city=${this.selectedCity}`)
      if (!response.ok) throw new Error('Failed to fetch scatter data')
      return await response.json()
    },

    // 统计方法
    getTotalFlow() {
      if (!this.trafficData.flowData) return 0
      const city = this.selectedCity
      const total = this.trafficData.flowData.reduce((sum, item) => {
        return sum + (item[city] || 0)
      }, 0)
      return total.toLocaleString()
    },

    getPeakHour() {
      if (!this.trafficData.flowData) return '-'
      const city = this.selectedCity
      let maxFlow = 0
      let peakHour = '-'
      
      this.trafficData.flowData.forEach(item => {
        if (item[city] > maxFlow) {
          maxFlow = item[city]
          peakHour = item.hour
        }
      })
      return peakHour
    },

    getAccuracy() {
      if (!this.trafficData.modelPerformance) return 0
      const model = this.trafficData.modelPerformance.find(m => 
        m.name.toLowerCase() === this.selectedModel.toLowerCase()
      )
      return model ? model.value.toFixed(1) : 0
    }
  }
}
</script>

<style scoped>
.traffic-dashboard {
  min-height: 100vh;
  padding: 35px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

/* 头部样式 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 30px 35px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dashboard-header h1 {
  color: #1a1a2e;
  font-size: 2.4rem;
  margin: 0;
  font-weight: 800;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 控制栏样式 */
.controls {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  font-size: 0.7rem;
  color: #6b7280;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.control-select, .date-picker {
  padding: 14px 18px;
  border: 2px solid #e5e7eb;
  border-radius: 14px;
  background: white;
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 140px;
  outline: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.control-select:hover, .date-picker:hover {
  border-color: #667eea;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.25);
  transform: translateY(-2px);
}

.control-select:focus, .date-picker:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
}

.control-select option {
  padding: 10px;
  font-weight: 500;
}

/* 加载和状态指示器 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: #f8f9fa;
  border-radius: 12px;
  color: #667eea;
  font-size: 14px;
  font-weight: 600;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #e8ecf1;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.data-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.data-badge.real {
  background: linear-gradient(135deg, #91cc75, #7cb85f);
  color: white;
  box-shadow: 0 4px 12px rgba(145, 204, 117, 0.3);
}

.data-badge.simulated {
  background: linear-gradient(135deg, #fac858, #f5a623);
  color: white;
  box-shadow: 0 4px 12px rgba(250, 200, 88, 0.3);
}

.badge-icon {
  font-size: 14px;
}

/* 数据切换按钮 */
.data-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.3px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  outline: none;
  min-width: 130px;
}

.data-toggle-btn.real {
  background: linear-gradient(135deg, #91cc75, #7cb85f);
  color: white;
  box-shadow: 0 4px 12px rgba(145, 204, 117, 0.3);
}

.data-toggle-btn.simulated {
  background: linear-gradient(135deg, #fac858, #f5a623);
  color: white;
  box-shadow: 0 4px 12px rgba(250, 200, 88, 0.3);
}

.data-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.data-toggle-btn:active {
  transform: translateY(0);
}

/* 统计概览卡片 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 26px 32px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  flex: 1;
  min-width: 0;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
  border-color: rgba(102, 126, 234, 0.3);
}

.stat-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  min-width: 60px;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  flex-shrink: 0;
  line-height: 1;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.stat-value {
  font-size: 1.7rem;
  font-weight: 800;
  color: #1a1a2e;
  line-height: 1.1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

/* 图表网格 */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28px;
}

/* 图表容器 */
.chart-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.chart-container:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
  border-color: rgba(102, 126, 234, 0.3);
}

.chart-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 22px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f3f7;
}

.chart-header h3 {
  color: #1a1a2e;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 12px;
  line-height: 1.3;
}

.chart-subtitle {
  color: #6b7280;
  font-size: 0.85rem;
  font-weight: 500;
  margin-left: 32px;
  letter-spacing: 0.3px;
}

.chart-body {
  flex: 1;
  min-height: 340px;
}

.chart-body.heatmap-body {
  min-height: 420px;
}

.full-width {
  grid-column: 1 / -1;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .traffic-dashboard {
    padding: 20px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 25px;
    padding: 25px;
  }
  
  .dashboard-header h1 {
    font-size: 1.9rem;
  }
  
  .controls {
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
  }
  
  .control-select, .date-picker {
    min-width: 120px;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .stat-card {
    padding: 20px 24px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .chart-grid {
    gap: 20px;
  }
  
  .chart-container {
    padding: 24px;
  }
}
</style>

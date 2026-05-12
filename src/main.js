import { createApp } from 'vue'
import App from './App.vue'
import ECharts from 'vue-echarts'
import * as echarts from 'echarts/core'
import {
  LineChart,
  BarChart,
  HeatmapChart,
  PieChart,
  ScatterChart
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  CalendarComponent,
  VisualMapComponent
} from 'echarts/components'
import {
  CanvasRenderer
} from 'echarts/renderers'

echarts.use([
  LineChart,
  BarChart,
  HeatmapChart,
  PieChart,
  ScatterChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent,
  CalendarComponent,
  VisualMapComponent,
  CanvasRenderer
])

const app = createApp(App)
app.component('v-chart', ECharts)
app.mount('#app')

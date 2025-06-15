<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

const data = ref([])
const loading = ref(false)
const error = ref(null)
const currentDate = ref('')

// 构建 API URL - 使用相对路径，会被代理转发
const apiUrl = computed(() => {
  return `/api/archives/${currentDate.value}.json`
})

// 获取当前日期并格式化为 YYYY/MM/DD
const getCurrentDate = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}/${month}/${day}`
}

const fetchData = async () => {
  loading.value = true
  error.value = null

  try {
    const dateStr = getCurrentDate()
    console.log('请求 URL:', apiUrl.value)
    const response = await fetch(apiUrl.value, {
        // `https://hentai.bgzo.cc/api/archives/${dateStr}.json`
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // 如果需要认证，可以添加 Authorization header
        // 'Authorization': 'Bearer your-token-here'
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    data.value = result

  } catch (err) {
    error.value = err.message
    console.error('API 请求失败:', err)
  } finally {
    loading.value = false
  }
}

// 组件挂载时设置当前日期
onMounted(() => {
  currentDate.value = getCurrentDate()
})

</script>

<template>
<!--  <div v-for="(today, index) in data">-->
<!--    <h1>-->

<!--    </h1>-->
<!--  </div>-->
  <div class="api-demo">
    <h3>API 数据展示</h3>
    <div class="controls">
      <button @click="fetchData" :disabled="loading">
        {{ loading ? '加载中...' : '获取数据' }}
      </button>
      <span class="date-info">请求日期: {{ currentDate }}</span>
    </div>

    <div v-if="error" class="error">
      错误: {{ error }}
    </div>

    <div v-if="data" class="data-display">
      <h4>API 响应数据:</h4>
      <pre>{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </div>

</template>

<style scoped>
.api-demo {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.controls {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.controls button {
  background: #007acc;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.controls button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.date-info {
  font-size: 14px;
  color: #666;
}

.error {
  background: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.data-display {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  margin-top: 15px;
}

.data-display pre {
  background: white;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}
</style>
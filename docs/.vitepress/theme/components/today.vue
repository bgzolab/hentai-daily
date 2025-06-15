<script setup lang="ts">
import { ref, onMounted, computed, nextTick  } from 'vue'
import {onContentUpdated, useData} from "vitepress";

// ========= Response Meta ==============
interface rssEntity {
  title: string,
  url: string,
  summary: string,
  timestamp: number
}
interface hentaiAPI {
    'Resources': rssEntity[],
    'News': rssEntity[],
    'DLsite Game Ranking': rssEntity[],
    'DLsite Voice Ranking': rssEntity[],
    'DLsite Comic Ranking': rssEntity[],
}
// =====================================

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
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    data.value = result
    updatePageOutline

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
  fetchData()
})


const { page } = useData()

const updatePageOutline = async () => {
  await nextTick()

  // 获取所有标题元素
  const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
    .map((el) => {
      const level = parseInt(el.tagName[1])
      const title = el.textContent || ''
      const anchor = el.id || title.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-')

      // 如果元素没有 id，添加一个
      if (!el.id) {
        el.id = anchor
      }

      return {
        level,
        title,
        anchor: `#${anchor}`
      }
    })

  // 更新页面的标题信息
  if (page.value) {
    ;(page.value as any).headers = headings
  }
}
onMounted(updatePageOutline)
onMounted(updatePageOutline)
onContentUpdated(updatePageOutline)

// onMounted(async () => {
//   await nextTick()
//
//   // 手动触发 VitePress 重新扫描页面标题
//   if (typeof window !== 'undefined') {
//     // 获取所有标题元素
//     const headers = document.querySelectorAll('h1, h2, h3, h4, h5, h6')
//
//     // 触发 VitePress 的目录更新事件
//     const event = new CustomEvent('vitepress:updateOutline', {
//       detail: { headers }
//     })
//     window.dispatchEvent(event)
//
//     // 或者尝试直接更新 VitePress 的内部状态
//     if (window.__vitepress) {
//       window.__vitepress.updateOutline?.()
//     }
//   }
// })

</script>

<template>
<!--    <div class="table-of-contents">-->
<!--    <h2>目录</h2>-->
<!--    <ul>-->
<!--      <li v-for="(today, index) in data" :key="index">-->
<!--        <a :href="`#section-${index}`">{{index}}</a>-->
<!--        <ul>-->
<!--          <li v-for="(entity, entity_index) in today" :key="entity_index">-->
<!--            <a :href="`#item-${index}-${entity_index}`">{{entity['title']}}</a>-->
<!--          </li>-->
<!--        </ul>-->
<!--      </li>-->
<!--    </ul>-->
<!--  </div>-->

    <div class="controls">
      <button @click="fetchData" :disabled="loading">
        {{ loading ? '加载中...' : '刷新' }}
      </button>
      <span class="date-info">请求日期: {{ currentDate }}</span>
    </div>

    <div v-if="error" class="error">
      错误: {{ error }}
    </div>

     <div v-for="(today, index) in data">
     <h2 :id="`section-${index}`">
       {{index}}
    </h2>

   <div v-for="(entity, entity_index) in today" :key="entity_index">
      <h3 :id="`item-${index}-${entity_index}`">
        <a :href="`${entity['url']}`" target="_blank">{{entity['title']}}</a>
      </h3>
      <div v-html="entity['summary']"></div>
    </div>
  </div>

</template>

<style scoped>

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
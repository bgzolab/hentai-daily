<script setup lang="ts">
import {ref, onMounted, computed, nextTick, reactive} from 'vue'
import {Content, onContentUpdated, useData} from "vitepress";

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
// FIXME: 凌晨怎么办？？？
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
    // updatePageOutline

  } catch (err) {
    error.value = err.message
    console.error('API 请求失败:', err)
  } finally {
    loading.value = false
  }
}

// 方案1的状态
const isCollapsed = ref(false)
const showAllItems = reactive<Record<string, boolean>>({})

const toggleItemsVisibility = (index: string) => {
  showAllItems[index] = !showAllItems[index]
}

// 组件挂载时设置当前日期
onMounted(() => {
  currentDate.value = getCurrentDate()
  fetchData()
})


// 更新目录
// const {page} = useData()
//
// const updatePageOutline = async () => {
//   await nextTick()
//
//   // 获取所有标题元素
//   const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
//       .map((el) => {
//         const level = parseInt(el.tagName[1])
//         const title = el.textContent || ''
//         const anchor = el.id || title.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-')
//
//         // 如果元素没有 id，添加一个
//         if (!el.id) {
//           el.id = anchor
//         }
//
//         return {
//           level,
//           title,
//           anchor: `#${anchor}`
//         }
//       })
//
//   // 更新页面的标题信息
//   if (page.value) {
//     ;(page.value as any).headers = headings
//   }
// }
// onMounted(updatePageOutline)
// onContentUpdated(updatePageOutline)
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
//       detail: {headers}
//     })
//     window.dispatchEvent(event)
//     console.log("更新")
//   }
// })
</script>

<template>
  <div class="controls">
    <button @click="fetchData" :disabled="loading">
      {{ loading ? '加载中...' : '刷新' }}
    </button>
    <span class="date-info">请求日期: {{ currentDate }}</span>
  </div>
  <div v-if="error" class="error">
    错误: {{ error }}
  </div>
  <!---------------------------------------------------------->

  <!--  <div class="table-of-contents">-->
  <!--    <h2>Table of contents</h2>-->
  <!--    <ul>-->
  <!--      <li v-for="(today, index) in data" :key="index">-->
  <!--        <a :href="`#section-${index}`">{{ index }}</a>-->
  <!--        <ul>-->
  <!--          <li v-for="(entity, entity_index) in today" :key="entity_index">-->
  <!--            <a :href="`#item-${index}-${entity_index}`">{{ entity['title'] }}</a>-->
  <!--          </li>-->
  <!--        </ul>-->
  <!--      </li>-->
  <!--    </ul>-->
  <!--  </div>-->
  <!--  -->

  <div class="toc-container">
    <div
        class="toc-header"
        @click="isCollapsed = !isCollapsed"
    >
      <h2>📖 Table of Contents</h2>
      <span class="collapse-icon">
        {{ isCollapsed ? '▶' : '▼' }}
      </span>
    </div>

    <div
        class="toc-content"
        :class="{ collapsed: isCollapsed }"
    >
      <ul class="toc-list">
        <li
            v-for="(today, index) in data"
            :key="index"
            class="toc-section"
        >
          <a
              :href="`#section-${index}`"
              class="section-link"
          >
            {{ index }} ({{ today.length }} 篇)
          </a>
          <ul class="toc-items">
            <li
                v-for="(entity, entity_index) in today.slice(0, showAllItems[index] ? undefined : 3)"
                :key="entity_index"
                class="toc-item"
            >
              <a
                  :href="`#item-${index}-${entity_index}`"
                  class="item-link"
                  :title="entity.title"
              >
                {{ entity.title }}
              </a>
            </li>
            <!-- 显示更多按钮 -->
            <li v-if="today.length > 3" class="show-more">
              <button
                  @click="toggleItemsVisibility(index)"
                  class="show-more-btn"
              >
                {{ showAllItems[index] ? '显示更少' : `显示更多 (${today.length - 3} 篇)` }}
              </button>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>


  <!---------------------------------------------------------->

  <div v-for="(today, index) in data">
    <h2 :id="`section-${index}`">
      {{ index }}
    </h2>

    <div v-for="(entity, entity_index) in today" :key="entity_index">
      <h3 :id="`item-${index}-${entity_index}`">
        <a :href="`${entity['url']}`" target="_blank">{{ entity['title'] }}</a>
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

/* 方案1样式 */
.toc-container {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin: 20px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  /*
    background: #f9fafb;
   */
  border-bottom: 1px solid grey;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.toc-header:hover {
  /**
  background: #f3f4f6;
   */
}

.toc-header h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
}

.collapse-icon {
  font-size: 14px;
  color: #6b7280;
  transition: transform 0.2s;
}

.toc-content {
  max-height: 400px;
  overflow-y: auto;
  transition: all 0.3s ease;
  padding: 16px;
}

.toc-content.collapsed {
  max-height: 0;
  padding: 0 16px;
  overflow: hidden;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-section {
  margin-bottom: 16px;
  padding-left: 8px;
  border-left: 3px solid #e5e7eb;
}

.section-link {
  display: block;
  font-weight: 600;
  color: #2563eb;
  text-decoration: none;
  padding: 4px 0;
  transition: color 0.2s;
}

.section-link:hover {
  color: #1d4ed8;
}

.toc-items {
  list-style: none;
  padding: 0;
  margin: 8px 0 0 0;
}

.toc-item {
  margin-bottom: 4px;
}

.item-link {
  display: block;
  color: #6b7280;
  text-decoration: none;
  font-size: 0.9rem;
  padding: 2px 0;
  line-height: 1.4;
  transition: color 0.2s;

  /* 文本截断 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-link:hover {
  color: #374151;
}

.show-more {
  margin-top: 8px;
}

.show-more-btn {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 4px 0;
  text-decoration: underline;
  transition: color 0.2s;
}

.show-more-btn:hover {
  color: #1d4ed8;
}

</style>
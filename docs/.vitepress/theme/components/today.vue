<script setup lang="ts">
import {ref, onMounted, computed, nextTick, reactive, UnwrapRef} from 'vue'
import {Content, onContentUpdated, useData} from "vitepress";

/**
 * Response Meta
 */
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

// 定义字段映射配置
const FIELD_CONFIG = {
  'Resources': {price: 'FREE', type: 'tip', ranking: false, desc: ""},
  'News': {price: 'FREE', type: 'tip', ranking: false, desc: ""},
  'DLsite Game Ranking': {price: 'PAID', type: 'danger', ranking: true, desc: ""},
  'DLsite Voice Ranking': {price: 'PAID', type: 'danger', ranking: true, desc: ""},
  'DLsite Comic Ranking': {price: 'PAID', type: 'danger', ranking: true, desc: ""},
} as const;

/**
 * Fields
 */

const data = ref<hentaiAPI>(null)
const loading = ref(false)
const error = ref(null)
const currentDate = ref('')
const tocCountLimit = 5
/**
 * 获取昨日凌晨的时间戳（本地时间）
 * 精确到秒（非毫秒）
 */
const getYesterdayMidnightTimestamp = (): number => {
  const now = new Date();
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  yesterday.setHours(0, 0, 0, 0);
  return yesterday.getTime() / 1000;
};

// 格式化时间戳为可读字符串
const formatTimestamp = (timestamp: number): string => {
  const date = new Date(timestamp);
  return date.toLocaleString(); // 或者使用更具体的格式化方法
};

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
    // 类型断言和验证
    if (isValidHentaiAPI(result)) {
      data.value = result as hentaiAPI
      // formatResponse(data.value) TODO 过滤
    } else {
      throw new Error('Invalid API response format')
    }

  } catch (err) {
    error.value = err.message
    console.error('API 请求失败:', err)
  } finally {
    loading.value = false
  }
}

const handleCardClick = (url: string) => {
  // NOTE: open in current tab
  // window.location.href = url
  window.open(url, '_blank')
  // NOTE: open new tab
}

const handleCardCss = (entity_index: number, index: string) => {
  if (!FIELD_CONFIG[index].ranking) {
    // no ranking no handle
    return 'card-style-common'
  }else {
    switch (entity_index) {
      case 0: return  'card-style-king'
      case 1: return  'card-style-silver'
      case 2: return  'card-style-bronze'
      case 3: return  'card-style-common'
      case 4: return  'card-style-common'
    }
  }
}

// 类型验证函数
function isValidHentaiAPI(obj: any): obj is hentaiAPI {
  if (!obj || typeof obj !== 'object') return false
  const requiredKeys: (keyof hentaiAPI)[] = [
    'Resources',
    'News',
    'DLsite Game Ranking',
    'DLsite Voice Ranking',
    'DLsite Comic Ranking'
  ]
  return requiredKeys.every(key => {
    const value = obj[key]
    return Array.isArray(value) && value.every(isValidRssEntity)
  })
}

function isValidRssEntity(obj: any): obj is rssEntity {
  return obj &&
      typeof obj === 'object' &&
      typeof obj.title === 'string' &&
      typeof obj.url === 'string' &&
      typeof obj.summary === 'string' &&
      typeof obj.timestamp === 'number'
}

const filterToday = (list: rssEntity[]) => {
  return list.filter(i => i.timestamp > getYesterdayMidnightTimestamp())
}

// 方案1的状态
const isCollapsed = ref(true)
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
  <!--  <div class="controls">-->
  <!--    <button @click="fetchData" :disabled="loading">-->
  <!--      {{ loading ? '加载中...' : '刷新' }}-->
  <!--    </button>-->
  <!--    <span class="date-info">请求日期: {{ currentDate }}</span>-->
  <!--  </div>-->
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
    <div class="toc-header" @click="isCollapsed = !isCollapsed">
      <h2>Table of Contents</h2>
      <span class="collapse-icon">
        {{ isCollapsed ? '▶' : '▼' }}
      </span>
    </div>

    <div class="toc-content"
         :class="{ collapsed: isCollapsed }">
      <ul class="toc-list">
        <li v-for="(today, index) in data"
            :key="index"
            class="toc-section">
          <a :href="`#section-${index}`"
             v-if="filterToday(today).length !== 0"
             class="section-link">
            {{ index }} ({{ filterToday(today).length }})
          </a>
          <ul class="toc-items">
            <li v-for="(entity, entity_index) in today.slice(0, showAllItems[index] ? undefined : tocCountLimit)"
                :key="entity_index"
                class="toc-item">
              <a :href="`#item-${index}-${entity_index}`"
                 v-if="entity.timestamp > getYesterdayMidnightTimestamp()"
                 class="item-link"
                 :title="entity.title">
                {{ entity.title }}
              </a>
            </li>
            <!-- 显示更多按钮 -->
            <li v-if="filterToday(today).length > tocCountLimit" class="show-more">
              <button
                  @click="toggleItemsVisibility(index)"
                  class="show-more-btn">
                {{ showAllItems[index] ? 'Show less' : `Show more(${filterToday(today).length - tocCountLimit})` }}
              </button>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>


  <!--------------------------Content-------------------------------->
  <div v-for="(today, index) in data">
    <h2 class="today-title" v-if="filterToday(today).length > 0" :id="`section-${index}`">
      {{ index }}
    </h2>
    {{ FIELD_CONFIG[index].desc }}
    <div v-for="(entity, entity_index) in today" :key="entity_index">
      <div v-if="entity.timestamp > getYesterdayMidnightTimestamp()">
        <div class="success-card" @click="handleCardClick(entity.url)">
          <div :class="`card-content ${handleCardCss(entity_index, index)} card-style`">
            <span class="card-header">
                <h3 :id="`item-${index}-${entity_index}`" class='card-title'>
                {{ entity.title === '' ? 'Untitled' : entity.title }}
                  <Badge :type="FIELD_CONFIG[index].type" :text="FIELD_CONFIG[index].price"/>
                </h3>
                <span class="card-datetime">{{ formatTimestamp(entity.timestamp * 1000) }}</span>
            </span>
            <div class="message" v-html="entity.summary"/>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped>

.today-title {
  text-align: center;
}

.success-card {
  border-radius: 20px;
  overflow: hidden;

  margin: 30px 0 30px 0;
  width: 100%;
  position: relative;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.success-card:hover {
  transform: scale(1.05) rotate(1deg);
  box-shadow: 0 12px 24px -8px gray;
  /**
  var(--vp-c-brand-1)
   */
}

.card-content {
  padding: 2rem 1.5rem;
  position: relative;
  height: fit-content;
}

.card-header {
  width: 100%;
  display: inline-block;
  margin-bottom: 1rem;
  color: var(--vp-c-text-1);
}

.message {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  line-height: 1.4;
  color: var(--vp-c-text-1);
}

.card-title {
  margin: 10px 0 10px 0;
  color: var(--vp-c-text-1);
}

.card-datetime {
  float: right;
}

.particle {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  animation: float 4s infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  50% {
    transform: translateY(-20px) translateX(10px);
    opacity: 1;
  }
}

@keyframes pop {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.success-card.animate {
  animation: pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}


.controls button {
  background: var(--vp-c-brand-3);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.error {
  background: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}


/* 目录样式 */
.toc-container {
  border: 1px solid var(--vp-c-bg-soft);
  border-radius: 20px;
  height: 100%;
  background-color: var(--vp-c-bg-soft);
  transition: border-color 0.25s, background-color 0.25s;
}

.toc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
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
  padding: 10px 0 10px 0;
  border-top: 0;
  font-weight: 600;
  color: var(--vp-c-text-1);
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
  color: var(--vp-c-brand-1);
  text-decoration: none;
  padding: 4px 0;
  transition: color 0.2s;
}

.section-link:hover {
  color: var(--vp-c-brand-3);
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
  color: var(--vp-c-text-2);
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
  color: var(--vp-c-brand-1);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 4px 0;
  text-decoration: underline;
  transition: color 0.2s;
}

.show-more-btn:hover {
  color: var(--vp-c-brand-3);
}

</style>
<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import CalHeatmap from "cal-heatmap";
import "cal-heatmap/cal-heatmap.css";
import { useToast } from "vue-toastification";
import Tooltip from "cal-heatmap/plugins/Tooltip";
import { useData } from "vitepress";

/**
 * Response Meta
 */
interface rssEntity {
  title: string;
  url: string;
  summary: string;
  timestamp: number;
}

interface hentaiAPI {
  Resources: rssEntity[];
  News: rssEntity[];
  "DLsite Game Ranking": rssEntity[];
  "DLsite Voice Ranking": rssEntity[];
  "DLsite Comic Ranking": rssEntity[];
}

type CategoryKey = keyof hentaiAPI;

const createEmptyApiData = (): hentaiAPI => ({
  Resources: [],
  News: [],
  "DLsite Game Ranking": [],
  "DLsite Voice Ranking": [],
  "DLsite Comic Ranking": [],
});

// 定义字段映射配置
const FIELD_CONFIG = {
  Resources: {
    price: "FREE",
    type: "tip",
    ranking: false,
    desc: "",
    rss: "https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/api/feeds/resources.xml",
  },
  News: {
    price: "FREE",
    type: "tip",
    ranking: false,
    desc: "",
    rss: "https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/api/feeds/news.xml",
  },
  "DLsite Game Ranking": {
    price: "PAID",
    type: "danger",
    ranking: true,
    desc: "",
    rss: "https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/api/feeds/dlsite-game-ranking.xml",
  },
  "DLsite Voice Ranking": {
    price: "PAID",
    type: "danger",
    ranking: true,
    desc: "",
    rss: "https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/api/feeds/dlsite-voice-ranking.xml",
  },
  "DLsite Comic Ranking": {
    price: "PAID",
    type: "danger",
    ranking: true,
    desc: "",
    rss: "https://raw.githubusercontent.com/bGZo/hentai-daily/refs/heads/vitepress/api/feeds/dlsite-comic-ranking.xml",
  },
} as const;

/**
 * Fields
 */

const data = ref<hentaiAPI>(createEmptyApiData());
// 日期
const currentDate = ref("");
// 当前选中的年份
const selectedYear = ref<number>(new Date().getFullYear());
// 可用的年份列表（从2023到当前年份）
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear();
  const years: number[] = [];
  for (let year = 2023; year <= currentYear; year++) {
    years.push(year);
  }
  return years.reverse(); // 降序排列，最新年份在前
});
const showContent = ref(true);
// 卡片布局：false 为单栏，true 为双栏
const isTwoColumn = ref(false);
// 消息通知
const toast = useToast();
// 是否是黑暗模式
const { isDark } = useData();
// 构建 API URL - 使用相对路径，会被代理转发
const apiUrl = computed(() => {
  return `/api/archives/${currentDate.value}.json`;
});

const YESTERDAY_ONLY_KEYS = new Set(["Resources", "News"]);

const CATEGORY_KEYS = Object.keys(FIELD_CONFIG) as CategoryKey[];

/**
 * 获取昨日凌晨的时间戳（本地时间）
 * 精确到秒（非毫秒）
 */
const getYesterdayMidnightTimestamp = (): number => {
  const yesterday = new Date(currentDate.value);
  yesterday.setDate(yesterday.getDate() - 1);
  yesterday.setHours(0, 0, 0, 0);
  return yesterday.getTime() / 1000;
};

/**
 * 获取当前日期凌晨的时间戳（本地时间）
 * 精确到秒（非毫秒）
 */
const getCurrentDayMidnightTimestamp = (): number => {
  const current = new Date(currentDate.value);
  current.setHours(0, 0, 0, 0);
  return current.getTime() / 1000;
};

// 格式化时间戳为可读字符串
const formatTimestamp = (timestamp: number): string => {
  const date = new Date(timestamp);
  return date.toLocaleString(); // 或者使用更具体的格式化方法
};

// 获取当前日期并格式化为 YYYY/MM/DD（用于 API 调用）
const getCurrentDate = (now: Date) => {
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}/${month}/${day}`;
};

// 格式化日期为 MM/DD 格式（用于显示）
const formatDisplayDate = (dateStr: string): string => {
  // dateStr 格式为 YYYY/MM/DD
  const [, month, day] = dateStr.split("/");
  return `${month}/${day}/`;
};

const fetchData = async () => {
  try {
    console.log("请求 URL:", apiUrl.value);
    const response = await fetch(apiUrl.value, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      showContent.value = false;
      data.value = createEmptyApiData();
      // error route
      if (404 == response.status) {
        toast.info("It seems not exist for today. Please check other days");
      } else {
        toast.error(
          `Except resonse with: ${response.status}, please contact with admin`,
        );
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      showContent.value = true;
    }

    const result = await response.json();
    // 类型断言和验证
    if (isValidHentaiAPI(result)) {
      data.value = result as hentaiAPI;
      // formatResponse(data.value) TODO 过滤
    } else {
      throw new Error("Invalid API response format");
    }
  } catch (err) {
    console.error("API 请求失败:", err);
  }
};

const clickCopyLink = (url: string) => {
  navigator.clipboard
    .writeText(url)
    .then(() => {
      toast.info("Copy link successful.");
    })
    .catch((e) => console.error(e));
};

const handleSubscribeClick = (index: keyof typeof FIELD_CONFIG) => {
  window.open(FIELD_CONFIG[index].rss, "_blank");
};

const handleCardClick = (url: string) => {
  // NOTE: open in current tab
  // window.location.href = url
  // NOTE: open new tab
  window.open(url, "_blank");
};

const handleCardCss = (
  entity_index: number,
  index: keyof typeof FIELD_CONFIG,
) => {
  if (!FIELD_CONFIG[index].ranking) {
    // no ranking no handle
    return "card-style-common";
  }

  const rankStyles = [
    "card-style-king",
    "card-style-silver",
    "card-style-bronze",
  ];
  return rankStyles[entity_index] ?? "card-style-common";
};

// 从 URL 提取根域名
const extractRootDomain = (url: string): string => {
  try {
    let normalizedUrl = url;
    // 处理 // 开头的 URL
    if (url.startsWith("//")) {
      normalizedUrl = "https:" + url;
    } else if (!url.startsWith("http://") && !url.startsWith("https://")) {
      normalizedUrl = "https://" + url;
    }

    const hostname = new URL(normalizedUrl).hostname;
    // 移除 www. 前缀并提取根域名（取最后两个部分）
    const parts = hostname.replace(/^www\./, "").split(".");
    return parts.length >= 2 ? parts.slice(-2).join(".") : parts.join(".");
  } catch {
    return url;
  }
};

// 类型验证函数
function isValidHentaiAPI(obj: any): obj is hentaiAPI {
  // if (!obj || typeof obj !== "object") return false;
  // const requiredKeys: (keyof hentaiAPI)[] = [
  //   "Resources",
  //   "News",
  //   "DLsite Game Ranking",
  //   "DLsite Voice Ranking",
  //   "DLsite Comic Ranking",
  // ];
  // return requiredKeys.every((key) => {
  //   const value = obj[key];
  //   return (
  //     null === value ||
  //     (Array.isArray(value) && value.every(isValidRssEntity))
  //   );
  // });
  return true; // 先假设所有响应都是有效的，后续可以根据实际情况调整
}

const shouldDisplayEntity = (
  category: CategoryKey,
  timestamp: number,
): boolean => {
  if (YESTERDAY_ONLY_KEYS.has(category)) {
    const start = getYesterdayMidnightTimestamp();
    const end = getCurrentDayMidnightTimestamp();
    return timestamp >= start && timestamp < end;
  }

  // Ranking 分类保持原逻辑
  return timestamp > getYesterdayMidnightTimestamp();
};

const getVisibleEntries = (
  category: CategoryKey,
  list: rssEntity[],
): rssEntity[] => {
  return list.filter((i) => shouldDisplayEntity(category, i.timestamp));
};

const visibleData = computed(() => {
  const result = createEmptyApiData();
  for (const category of CATEGORY_KEYS) {
    result[category] = getVisibleEntries(category, data.value[category]);
      }
  return result;
});

const refreshToday = (timestamp?: number) => {
  if (timestamp) {
    currentDate.value = getCurrentDate(new Date(timestamp));
  } else {
    currentDate.value = getCurrentDate(new Date());
  }
  fetchData();
};

// 检查指定日期是否存在日志
const checkDateExists = async (dateStr: string): Promise<boolean> => {
  // try {
  //   const response = await fetch(`/api/archives/${dateStr}.json`, {
  //     method: "GET",
  //   });
  //   return response.ok;
  // } catch {
  //   return false;
  // }
  return true; // 先假设所有日期都存在，后续可以根据实际情况调整
};

function createCalHeatmap() {
  const cal = new CalHeatmap();
  // 根据选中的年份计算起始和结束日期，显示整个年份的12个月
  const startDate = new Date(selectedYear.value, 1, 1); // 该年的1月1日
  const endDate = new Date(selectedYear.value, 12, 31); // 该年的12月31日

  cal.paint(
    {
      itemSelector: "#cal-heatmap",
      domain: {
        type: "month",
      },
      subDomain: {
        type: "ghDay",
      },
      date: {
        start: startDate,
        end: endDate,
      },
      data: {
        source: "/api/count.json",
        x: "date",
        y: "value",
      },
      scale: {
        color: {
          range: ["#9be9a8", "#40c463", "#30a14e", "#216e39"],
          domain: [0, 30],
        },
      },
      theme: isDark.value ? "dark" : "light",
    },
    [
      [
        Tooltip,
        {
          text: (t: number) => `${new Date(t).toLocaleDateString()}`,
        },
      ],
    ],
  );

  cal.on("click", ((event: any, timestamp: number, value: any) => {
    console.log("click" + new Date(timestamp).toLocaleDateString());
    if (timestamp > new Date().getTime()) {
      toast.info("The future is yours. Check it in few days later.");
    } else {
      const clickedDate = new Date(timestamp);
      // 如果点击的日期年份与当前选中年份不同，更新年份
      if (clickedDate.getFullYear() !== selectedYear.value) {
        selectedYear.value = clickedDate.getFullYear();
      }
      refreshToday(timestamp);
    }
  }) as any); // 关键：使用 as any 绕过类型检查
  return cal;
}

// 组件挂载时设置当前日期
onMounted(() => {
  console.log("1绘制为 ", isDark);
  refreshToday();

  let cal: any = null;

  const initCalHeatmap = () => {
    // 销毁旧的热力图
    if (cal) {
      cal.destroy();
    }
    // 清空容器
    const container = document.querySelector("#cal-heatmap");
    if (container) {
      container.innerHTML = "";
    }
    // 创建新热力图
    cal = createCalHeatmap();
  };

  initCalHeatmap();

  // 监听年份变化，重新绘制图表并加载该年的数据
  watch(selectedYear, async (newYear, oldYear) => {
    console.log("年份已更新为 ", newYear);

    // 构造该年同月同日的日期
    const today = new Date();
    const newDate = new Date(newYear, today.getMonth(), today.getDate());
    const newDateStr = getCurrentDate(newDate);

    // 检查新日期是否存在日志
    const exists = await checkDateExists(newDateStr);
    if (!exists) {
      // 数据不存在，恢复到旧年份
      selectedYear.value = oldYear;
      toast.warning(`No logs found for ${newDateStr}. Year reverted.`);
      return;
    }

    // 数据存在，重新绘制图表并加载数据
    initCalHeatmap();
    refreshToday(newDate.getTime());
  });

  // 监听黑暗模式变化，重新渲染图表
  watch(isDark, (dark) => {
    console.log("绘制为 ", dark);
    initCalHeatmap();
  });
});
</script>

<template>
  <div class="today-title">
    <span class="hero">Hentai Daily</span>
    <div class="date-selector">
      <span class="date">{{ formatDisplayDate(currentDate) }}</span>
      <select v-model.number="selectedYear" class="year-select">
        <option v-for="year in availableYears" :key="year" :value="year">
          {{ year }}
        </option>
      </select>
    </div>
  </div>
  <!-------------------------HeatMap--------------------------------->
  <div class="heatmap-scroll">
    <div id="cal-heatmap"></div>
  </div>
  <!-------------------------Actions Bar---------------------------->
  <div class="actions-bar">
    <span class="label">Double Columns</span>
    <button
      class="VPSwitch layout-switch"
      type="button"
      role="switch"
      :aria-checked="isTwoColumn"
      :title="isTwoColumn ? '切换为单栏' : '切换为双栏'"
      @click="isTwoColumn = !isTwoColumn"
    >
      <span class="check">
        <span class="icon">
          <span class="single-col"></span>
          <span class="two-col"></span>
        </span>
      </span>
    </button>
  </div>
  <div class="today-layout">
    <main class="today-main">
      <!--------------------------Content-------------------------------->
      <div
        v-for="(entries, index) in visibleData"
        :key="`today-${index}-${entries.length}`"
      >
        <h2
          class="content-title"
          v-if="entries.length > 0"
          :id="`section-${index}`"
        >
          {{ index }}
          <Badge
            type="warning"
            text="subscribe"
            @click="handleSubscribeClick(index)"
          />
        </h2>
        {{ FIELD_CONFIG[index].desc }}

        <div class="cards-grid" :class="{ 'cards-grid--two': isTwoColumn }">
          <div
            v-for="(entity, entity_index) in entries"
            :key="`${entity.url}-${entity_index}`"
            class="card-item"
          >
            <div class="card">
              <div class="card-wrapper">
                <div
                  :class="`card-content ${handleCardCss(entity_index, index)} card-style`"
                  @click="handleCardClick(entity.url)"
                >
                  <span class="card-header">
                    <h3
                      :id="`item-${index}-${entity_index}`"
                      class="card-title"
                    >
                      {{ entity.title === "" ? "Untitled" : entity.title }}
                      <Badge
                        :type="FIELD_CONFIG[index].type"
                        :text="extractRootDomain(entity.url)"
                      />
                    </h3>
                    <span class="card-datetime">{{
                      formatTimestamp(entity.timestamp * 1000)
                    }}</span>
                  </span>
                  <div class="message" v-html="entity.summary" />

                  <!-- 卡片底部按钮 -->
                  <div class="card-actions">
                    <button
                      class="action-btn action-copy"
                      title="Copy Link"
                      @click.stop="clickCopyLink(entity.url)"
                    >
                      <svg
                        t="1772717415932"
                        class="icon icon-svg"
                        viewBox="0 0 1024 1024"
                        version="1.1"
                        xmlns="http://www.w3.org/2000/svg"
                        p-id="1622"
                        width="200"
                        height="200"
                      >
                        <path
                          d="M931.882 131.882l-103.764-103.764A96 96 0 0 0 760.236 0H416c-53.02 0-96 42.98-96 96v96H160c-53.02 0-96 42.98-96 96v640c0 53.02 42.98 96 96 96h448c53.02 0 96-42.98 96-96v-96h160c53.02 0 96-42.98 96-96V199.764a96 96 0 0 0-28.118-67.882zM596 928H172a12 12 0 0 1-12-12V300a12 12 0 0 1 12-12h148v448c0 53.02 42.98 96 96 96h192v84a12 12 0 0 1-12 12z m256-192H428a12 12 0 0 1-12-12V108a12 12 0 0 1 12-12h212v176c0 26.51 21.49 48 48 48h176v404a12 12 0 0 1-12 12z m12-512h-128V96h19.264c3.182 0 6.234 1.264 8.486 3.514l96.736 96.736a12 12 0 0 1 3.514 8.486V224z"
                          p-id="1623"
                          fill="#8a8a8a"
                        ></path>
                      </svg>
                    </button>
                    <button
                      class="action-btn action-open"
                      title="Open Link"
                      @click.stop="handleCardClick(entity.url)"
                    >
                      <svg
                        t="1772716796795"
                        class="icon icon-svg"
                        viewBox="0 0 1024 1024"
                        version="1.1"
                        xmlns="http://www.w3.org/2000/svg"
                        p-id="6502"
                        width="200"
                        height="200"
                      >
                        <path
                          d="M819.2 887.466667H136.533333V204.8h341.333334V68.266667H136.533333a136.533333 136.533333 0 0 0-136.533333 136.533333v682.666667a136.533333 136.533333 0 0 0 136.533333 136.533333h682.666667a136.533333 136.533333 0 0 0 136.533333-136.533333V546.133333h-136.533333v341.333334z"
                          fill="#8a8a8a"
                          p-id="6503"
                        ></path>
                        <path
                          d="M955.733333 0h-273.066666a68.266667 68.266667 0 0 0 0 136.533333h108.202666L421.2736 506.129067a68.266667 68.266667 0 1 0 96.597333 96.597333L887.466667 233.130667V341.333333a68.266667 68.266667 0 0 0 136.533333 0V68.266667a68.266667 68.266667 0 0 0-68.266667-68.266667z"
                          fill="#8a8a8a"
                          p-id="6504"
                        ></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-------------------------TOC--------------------------------->
    <aside v-show="showContent" class="toc-aside">
      <div class="toc-container">
        <div class="toc-header">
          <h2>Table of Contents</h2>
        </div>
        <div class="toc-content">
          <ul class="toc-list">
            <li
              v-for="(entries, index) in visibleData"
              :key="index"
              class="toc-section"
            >
              <a
                :href="`#section-${index}`"
                v-if="entries.length !== 0"
                class="section-link"
              >
                {{ index }} ({{ entries.length }})
              </a>
              <ul class="toc-items">
                <li
                  v-for="(entity, entity_index) in entries"
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
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.today-layout {
  display: block;
}

.today-main {
  min-width: 0;
}

.toc-aside {
  display: none;
}

@media (min-width: 1280px) {
  .toc-aside {
    display: flex;
    position: fixed;
    top: calc(var(--vp-nav-height) + 24px);
    right: max(150px, calc((100vw - var(--vp-layout-max-width)) / 2 + 200px));
    width: 256px;
    height: calc(100vh - var(--vp-nav-height) - 48px);
    overflow: hidden;
    z-index: 10;
  }
}

.heatmap-scroll {
  overflow-x: auto;
  width: 100%;
}

#cal-heatmap {
  width: 100%;
  min-width: 100%;
  margin: 0;
}

.today-title {
  width: 100%;
  margin: 10px 0 10px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .hero {
    color: var(--vp-home-hero-name-color);
    font-size: 2em;
    font-weight: bold;
  }

  .date-selector {
    display: flex;
    align-items: center;
    white-space: nowrap;
  }

  .date {
    color: var(--vp-c-text-1);
    font-size: 1em;
    min-width: 80px;
    text-align: right;
  }

  .year-select {
    padding: 6px 28px 6px 0;
    border: none;
    background-color: transparent;
    color: var(--vp-c-text-1);
    font-size: 1em;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .year-select:hover {
    border-bottom-color: var(--vp-c-divider);
  }

  .year-select:focus {
    outline: none;
    border-bottom-color: var(--vp-c-brand-1);
  }
}

/* 操作栏 */
.actions-bar {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 12px 0;
  margin-bottom: 8px;
  .label {
    color: var(--vp-c-text-1);
    font-size: 0.9em;
    margin-right: 8px;
  }
}

/* VPSwitch 风格的布局切换按钮 */
.VPSwitch.layout-switch {
  position: relative;
  display: inline-block;
  border-radius: 11px;
  width: 40px;
  height: 22px;
  background-color: var(--vp-c-default-soft);
  border: 1px solid var(--vp-c-divider);
  cursor: pointer;
  transition:
    background-color 0.25s,
    border-color 0.25s;
  margin-right: 28px;
}

.VPSwitch.layout-switch:hover {
  border-color: var(--vp-c-gray);
}

.VPSwitch.layout-switch[aria-checked="true"] {
  background-color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
}

.VPSwitch.layout-switch .check {
  position: absolute;
  top: 1px;
  left: 1px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: var(--vp-c-bg);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
  transition: transform 0.25s;
}

.VPSwitch.layout-switch[aria-checked="true"] .check {
  transform: translateX(18px);
}

.VPSwitch.layout-switch .icon {
  position: relative;
  display: block;
  width: 18px;
  height: 18px;
  line-height: 18px;
  text-align: center;
}

.VPSwitch.layout-switch .single-col,
.VPSwitch.layout-switch .two-col {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  transition: opacity 0.25s;
}

.VPSwitch.layout-switch .single-col {
  opacity: 1;
}

.VPSwitch.layout-switch .two-col {
  opacity: 0;
}

.VPSwitch.layout-switch[aria-checked="true"] .single-col {
  opacity: 0;
}

.VPSwitch.layout-switch[aria-checked="true"] .two-col {
  opacity: 1;
}

#cal-heatmap {
  margin: 10px 0 20px 0;
}

.content-title {
  text-align: left;
}

.content-title:not(:first-of-type) {
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 32px;
  margin-top: 32px;
}

.card {
  border-radius: 20px;
  overflow: visible;
  margin: 20px 0;
  width: 100%;
  position: relative;
  cursor: pointer;
}

.card-item {
  width: 100%;
  /* 固定容器，为动画预留空间 */
  padding: 15px;
  box-sizing: border-box;
}

/* 内部包装层，限制动画范围 */
.card-wrapper {
  position: relative;
  width: 100%;
  min-height: 200px;
  overflow: hidden;
  border-radius: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, box-shadow;
}

.card-wrapper:hover {
  transform: scale(1.02) translateY(-4px) rotate(0.5deg);
  box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.3);
}

.cards-grid--two {
  column-count: 2;
  column-gap: 20px;
}

.cards-grid--two .card-item {
  width: 100%;
  break-inside: avoid;
  page-break-inside: avoid; /* 兼容旧浏览器 */
  -webkit-column-break-inside: avoid; /* Safari */
  margin-bottom: 20px;
}

.cards-grid--two .card {
  margin: 0;
  width: 100%;
}

.cards-grid--two .card-item {
  padding: 10px;
}

@media (max-width: 960px) {
  .cards-grid--two {
    column-count: 1;
  }
  .actions-bar {
    display: none;
  }
}

/* 卡片底部操作按钮面板 */
.card-actions {
  position: relative;
  display: flex;
  margin-top: 1rem;
  height: 44px;
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
  pointer-events: none;
  transition:
    opacity 0.25s ease,
    transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-wrapper:hover .card-actions {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.action-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  color: var(--vp-c-text-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

/* 按钮之间的间距 */
.action-btn + .action-btn {
  margin-left: 8px;
}

.icon-svg {
  width: 24px;
  height: 24px;
  display: block;
  transition: transform 0.2s ease;
}

.action-btn:hover .icon-svg {
  transform: scale(1.1);
}

.icon-svg path {
  fill: var(--vp-c-text-1);
  transition: fill 0.2s ease;
}

.action-btn:hover .icon-svg path {
  fill: var(--vp-c-brand-1);
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
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  line-height: 1.4;
  color: var(--vp-c-text-1);
}

:deep(.message img) {
  display: block;
  width: calc(100% + 3rem);
  max-width: none;
  height: auto;
  margin: 0.75rem -1.5rem;
  object-fit: cover;
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
  0%,
  100% {
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

.card.animate {
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
  display: flex;
  flex-direction: column;
  position: static;
  border-left: 1px solid var(--vp-c-divider);
  padding-left: 16px;
  height: 100%;
}

.toc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 0 12px 0;
  cursor: pointer;
  user-select: none;
}

.toc-header h2 {
  margin: 0;
  padding: 0;
  border-top: 0;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  /* text-transform: uppercase; */
  color: var(--vp-c-text-2);
}

.collapse-icon {
  font-size: 12px;
  color: var(--vp-c-text-3);
  transition: transform 0.2s;
}

.toc-content {
  flex: 1;
  overflow-y: auto;
  transition: all 0.3s ease;
  padding: 0 0 8px 0;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-section {
  margin-bottom: 12px;
  padding-left: 0;
  border-left: 0;
}

.section-link {
  display: block;
  font-weight: 600;
  font-size: 13px;
  color: var(--vp-c-brand-1);
  text-decoration: none;
  padding: 2px 0;
  transition: color 0.2s;
}

.section-link:hover {
  color: var(--vp-c-brand-2);
}

.toc-items {
  list-style: none;
  padding: 0 0 0 12px;
  margin: 8px 0 0 0;
}

.toc-item {
  margin-bottom: 2px;
}

.item-link {
  display: block;
  color: var(--vp-c-text-3);
  text-decoration: none;
  font-size: 12px;
  padding: 2px 0;
  line-height: 1.4;
  transition: color 0.2s;

  /* 文本截断 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-link:hover {
  color: var(--vp-c-text-1);
}

.show-more {
  margin-top: 8px;
}
</style>

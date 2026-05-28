<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import CalHeatmap from "cal-heatmap";
import "cal-heatmap/cal-heatmap.css";
import { useToast } from "vue-toastification";
import Tooltip from "cal-heatmap/plugins/Tooltip";
import { useData } from "vitepress";
import TodayFeedSection from "./today/TodayFeedSection.vue";
import TodayRankingSection from "./today/TodayRankingSection.vue";

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

interface countEntity {
  date: string;
  value: number;
}

interface sectionModelEntity {
  key: CategoryKey;
  title: string;
  variant: SectionVariant;
  entries: rssEntity[];
  rss: string;
  badgeType: string;
  avatarSlots: number;
  topCount: number;
  desc: string;
}

const COUNT_JSON_URL = "/api/count.json";
let countDataCache: countEntity[] | null = null;
let countDataPromise: Promise<countEntity[]> | null = null;

type CategoryKey = keyof hentaiAPI;

const createEmptyApiData = (): hentaiAPI => ({
  Resources: [],
  News: [],
  "DLsite Game Ranking": [],
  "DLsite Voice Ranking": [],
  "DLsite Comic Ranking": [],
});

type SectionVariant = "feed" | "ranking";

interface sectionConfigEntity {
  price: string;
  type: string;
  ranking: boolean;
  variant: SectionVariant;
  desc: string;
  rss: string;
  avatarSlots: number;
  topCount: number;
}

// 定义字段映射配置
const SECTION_CONFIG: Record<CategoryKey, sectionConfigEntity> = {
  Resources: {
    price: "FREE",
    type: "tip",
    ranking: false,
    variant: "feed",
    desc: "",
    rss: "https://raw.githubusercontent.com/bgzo/hentai-daily/refs/heads/vitepress/api/feeds/resources.xml",
    avatarSlots: 4,
    topCount: 0,
  },
  News: {
    price: "FREE",
    type: "tip",
    ranking: false,
    variant: "feed",
    desc: "",
    rss: "https://raw.githubusercontent.com/bgzo/hentai-daily/refs/heads/vitepress/api/feeds/news.xml",
    avatarSlots: 4,
    topCount: 0,
  },
  "DLsite Game Ranking": {
    price: "PAID",
    type: "danger",
    ranking: true,
    variant: "ranking",
    desc: "",
    rss: "https://raw.githubusercontent.com/bgzo/hentai-daily/refs/heads/vitepress/api/feeds/dlsite-game-ranking.xml",
    avatarSlots: 0,
    topCount: 3,
  },
  "DLsite Voice Ranking": {
    price: "PAID",
    type: "danger",
    ranking: true,
    variant: "ranking",
    desc: "",
    rss: "https://raw.githubusercontent.com/bgzo/hentai-daily/refs/heads/vitepress/api/feeds/dlsite-voice-ranking.xml",
    avatarSlots: 0,
    topCount: 3,
  },
  "DLsite Comic Ranking": {
    price: "PAID",
    type: "danger",
    ranking: true,
    variant: "ranking",
    desc: "",
    rss: "https://raw.githubusercontent.com/bgzo/hentai-daily/refs/heads/vitepress/api/feeds/dlsite-comic-ranking.xml",
    avatarSlots: 0,
    topCount: 3,
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
// 热力图 count.json 原始数据缓存
const heatmapCountData = ref<countEntity[]>([]);
// 热力图可用日期集合（来自 /api/count.json）
const availableHeatmapDates = ref<Set<string>>(new Set());
// 消息通知
const toast = useToast();
// 是否是黑暗模式
const { isDark } = useData();
// 构建 API URL - 使用相对路径，会被代理转发
const apiUrl = computed(() => {
  return `/api/archives/${currentDate.value}.json`;
});

const YESTERDAY_ONLY_KEYS = new Set(["Resources", "News"]);

const CATEGORY_KEYS = Object.keys(SECTION_CONFIG) as CategoryKey[];

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

const formatDateKey = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const loadAvailableHeatmapDates = async () => {
  try {
    if (countDataCache) {
      heatmapCountData.value = countDataCache;
      availableHeatmapDates.value = new Set(
        countDataCache
          .filter((item) => typeof item?.date === "string")
          .map((item) => item.date),
      );
      return;
    }

    if (!countDataPromise) {
      countDataPromise = (async () => {
        const response = await fetch(COUNT_JSON_URL, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch count.json: ${response.status}`);
        }

        const result = (await response.json()) as countEntity[];
        return result;
      })();
    }

    const result = await countDataPromise;
    countDataCache = result;
    heatmapCountData.value = result;
    availableHeatmapDates.value = new Set(
      result
        .filter((item) => typeof item?.date === "string")
        .map((item) => item.date),
    );
  } catch (err) {
    console.error("加载 count.json 失败:", err);
    heatmapCountData.value = [];
    availableHeatmapDates.value = new Set();
  } finally {
    countDataPromise = null;
  }
};

const isDateInCountData = (timestamp: number): boolean => {
  const dateKey = formatDateKey(new Date(timestamp));
  return availableHeatmapDates.value.has(dateKey);
};

const hasArchiveData = (archiveDate: string): boolean => {
  // archiveDate: YYYY/MM/DD -> count.json key: YYYY-MM-DD
  const dateKey = archiveDate.replace(/\//g, "-");
  return availableHeatmapDates.value.has(dateKey);
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

const handleSubscribeClick = (index: CategoryKey) => {
  window.open(SECTION_CONFIG[index].rss, "_blank");
};

const handleCardClick = (url: string) => {
  // NOTE: open in current tab
  // window.location.href = url
  // NOTE: open new tab
  window.open(url, "_blank");
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

const sectionModels = computed<sectionModelEntity[]>(() => {
  return CATEGORY_KEYS.map((category) => {
    const config = SECTION_CONFIG[category];

    return {
      key: category,
      title: category,
      variant: config.variant,
      entries: getVisibleEntries(category, data.value[category]),
      rss: config.rss,
      badgeType: config.type,
      avatarSlots: config.avatarSlots,
      topCount: config.topCount,
      desc: config.desc,
    };
  });
});

const refreshToday = (timestamp?: number) => {
  const targetDate = timestamp
    ? getCurrentDate(new Date(timestamp))
    : getCurrentDate(new Date());

  currentDate.value = targetDate;

  if (!hasArchiveData(targetDate)) {
    showContent.value = false;
    data.value = createEmptyApiData();
    return;
  }
  fetchData();
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
        source: heatmapCountData.value,
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

  cal.on("click", ((_event: any, timestamp: number, _value: any) => {
    console.log("click" + new Date(timestamp).toLocaleDateString());
    // 以 count.json 为准：只有存在于统计数据中的日期才允许跳转
    if (!isDateInCountData(timestamp)) {
      toast.info("No archived data for this day yet. Please try another date.");
      return;
    }

    const clickedDate = new Date(timestamp);
    // 如果点击的日期年份与当前选中年份不同，更新年份
    if (clickedDate.getFullYear() !== selectedYear.value) {
      selectedYear.value = clickedDate.getFullYear();
    }
    refreshToday(timestamp);
  }) as any); // 关键：使用 as any 绕过类型检查
  return cal;
}

// 组件挂载时设置当前日期
onMounted(async () => {
  console.log("绘制为 ", isDark);
  await loadAvailableHeatmapDates();
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

    // 数据存在，重新绘制图表并加载数据
    initCalHeatmap();

    // 检查新日期是否存在日志
    const exists = await hasArchiveData(newDateStr);
    if (!exists) {
      // 数据不存在，恢复到旧年份
      toast.info(`No logs found for ${newDateStr}.`);
      return;
    }

    // 缓存是否存在这天的结果，存在就请求，不存在不请求，避免404请求
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
  <div class="today-layout">
    <main class="today-main">
      <!--------------------------Content-------------------------------->
      <component
        :is="section.variant === 'feed' ? TodayFeedSection : TodayRankingSection"
        v-for="section in sectionModels"
        :key="`today-${section.key}-${section.entries.length}`"
        :section-key="section.key"
        :title="section.title"
        :entries="section.entries"
        :desc="section.desc"
        :badge-type="section.badgeType"
        :rss="section.rss"
        :avatar-slots="section.avatarSlots"
        @open="handleCardClick"
        @copy="clickCopyLink"
      />
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
              v-for="section in sectionModels"
              :key="section.key"
              class="toc-section"
            >
              <a
                :href="`#section-${section.key}`"
                v-if="section.entries.length !== 0"
                class="section-link"
              >
                {{ section.title }} ({{ section.entries.length }})
              </a>
              <ul class="toc-items">
                <li
                  v-for="(entity, entity_index) in section.entries"
                  :key="entity_index"
                  class="toc-item"
                >
                  <a
                    :href="`#item-${section.key}-${entity_index}`"
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

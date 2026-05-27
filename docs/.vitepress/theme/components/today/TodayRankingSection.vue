<script setup lang="ts">
import { computed } from "vue";
import {
  extractFirstImageFromSummary,
  extractTextFromSummary,
} from "./summary";

interface rssEntity {
  title: string;
  url: string;
  summary: string;
  timestamp: number;
}

const props = defineProps<{
  sectionKey: string;
  title: string;
  entries: rssEntity[];
  desc: string;
  badgeType: string;
  rss: string;
  isTwoColumn: boolean;
}>();

const emit = defineEmits<{
  open: [url: string];
  copy: [url: string];
}>();

const topEntries = computed(() => props.entries.slice(0, 3));
const otherEntries = computed(() => props.entries.slice(3));

const formatTimestamp = (timestamp: number): string => {
  return new Date(timestamp * 1000).toLocaleString();
};

const getRankingAccent = (rank: number): string => {
  if (rank === 1) {
    return "ranking-accent--gold";
  }

  if (rank === 2) {
    return "ranking-accent--silver";
  }

  if (rank === 3) {
    return "ranking-accent--bronze";
  }

  return "ranking-accent--default";
};

const getFallbackLabel = (rank: number): string => {
  return props.title
    .replace("DLsite ", "")
    .replace(" Ranking", "")
    .concat(` • Rank #${rank}`);
};

const handleOpen = (url: string): void => {
  emit("open", url);
};

const handleCopy = (url: string): void => {
  emit("copy", url);
};

const handleSubscribe = (): void => {
  window.open(props.rss, "_blank");
};
</script>

<template>
  <section class="ranking-section">
    <header
      v-if="entries.length > 0"
      :id="`section-${sectionKey}`"
      class="ranking-section__header"
    >
      <div class="ranking-section__heading-main">
        <span class="ranking-section__eyebrow">Leaderboard Board</span>
        <h2 class="content-title">{{ title }}</h2>
        <p class="ranking-section__meta">{{ entries.length }} ranked entries</p>
      </div>
      <button
        type="button"
        class="subscribe-pill"
        :class="`subscribe-pill--${badgeType}`"
        @click="handleSubscribe"
      >
        subscribe
      </button>
    </header>
    <p v-if="desc" class="ranking-section__desc">{{ desc }}</p>

    <div v-if="topEntries.length > 0" class="ranking-top">
      <article
        v-if="topEntries[0]"
        :id="`item-${sectionKey}-0`"
        class="ranking-hero"
        :class="getRankingAccent(1)"
      >
        <div class="ranking-hero__body" @click="handleOpen(topEntries[0].url)">
          <img
            v-if="extractFirstImageFromSummary(topEntries[0].summary)"
            class="ranking-media ranking-media--hero"
            :src="extractFirstImageFromSummary(topEntries[0].summary) || undefined"
            :alt="topEntries[0].title === '' ? 'Untitled ranking preview' : topEntries[0].title"
          />
          <div v-else class="ranking-media ranking-media--fallback">
            {{ getFallbackLabel(1) }}
          </div>
          <span class="ranking-badge" :class="getRankingAccent(1)">#1</span>
          <h3 class="ranking-hero__title">
            {{ topEntries[0].title === "" ? "Untitled" : topEntries[0].title }}
          </h3>
          <p class="ranking-hero__summary">{{ extractTextFromSummary(topEntries[0].summary) }}</p>
          <span class="ranking-hero__time">{{ formatTimestamp(topEntries[0].timestamp) }}</span>
        </div>
        <div class="ranking-card__actions">
          <button type="button" @click="handleCopy(topEntries[0].url)">Copy</button>
          <button type="button" @click="handleOpen(topEntries[0].url)">Open</button>
        </div>
      </article>

      <div class="ranking-secondary">
        <article
          v-for="(entity, entityIndex) in topEntries.slice(1)"
          :id="`item-${sectionKey}-${entityIndex + 1}`"
          :key="`${entity.url}-${entityIndex + 1}`"
          class="ranking-secondary__card"
          :class="getRankingAccent(entityIndex + 2)"
        >
          <div class="ranking-secondary__body" @click="handleOpen(entity.url)">
            <img
              v-if="extractFirstImageFromSummary(entity.summary)"
              class="ranking-media"
              :src="extractFirstImageFromSummary(entity.summary) || undefined"
              :alt="entity.title === '' ? 'Untitled ranking preview' : entity.title"
            />
            <div v-else class="ranking-media ranking-media--fallback">
              {{ getFallbackLabel(entityIndex + 2) }}
            </div>
            <span class="ranking-badge" :class="getRankingAccent(entityIndex + 2)">#{{ entityIndex + 2 }}</span>
            <h3 class="ranking-secondary__title">
              {{ entity.title === "" ? "Untitled" : entity.title }}
            </h3>
            <p class="ranking-secondary__summary">{{ extractTextFromSummary(entity.summary) }}</p>
            <span class="ranking-secondary__time">{{ formatTimestamp(entity.timestamp) }}</span>
          </div>
          <div class="ranking-card__actions">
            <button type="button" @click="handleCopy(entity.url)">Copy</button>
            <button type="button" @click="handleOpen(entity.url)">Open</button>
          </div>
        </article>
      </div>
    </div>

    <div
      v-if="otherEntries.length > 0"
      class="ranking-rows"
      :class="{ 'ranking-rows--two': isTwoColumn }"
    >
      <article
        v-for="(entity, entityIndex) in otherEntries"
        :id="`item-${sectionKey}-${entityIndex + 3}`"
        :key="`${entity.url}-${entityIndex + 3}`"
        class="ranking-row"
      >
        <div class="ranking-row__body" @click="handleOpen(entity.url)">
          <span class="ranking-row__rank">#{{ entityIndex + 4 }}</span>
          <img
            v-if="extractFirstImageFromSummary(entity.summary)"
            class="ranking-media ranking-media--row"
            :src="extractFirstImageFromSummary(entity.summary) || undefined"
            :alt="entity.title === '' ? 'Untitled ranking preview' : entity.title"
          />
          <div v-else class="ranking-media ranking-media--fallback ranking-media--row-fallback">
            {{ entityIndex + 4 }}
          </div>
          <div class="ranking-row__content">
            <h3 class="ranking-row__title">
              {{ entity.title === "" ? "Untitled" : entity.title }}
            </h3>
            <p class="ranking-row__summary">{{ extractTextFromSummary(entity.summary) }}</p>
          </div>
          <span class="ranking-row__time">{{ formatTimestamp(entity.timestamp) }}</span>
        </div>
        <div class="ranking-card__actions">
          <button type="button" @click="handleCopy(entity.url)">Copy</button>
          <button type="button" @click="handleOpen(entity.url)">Open</button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.ranking-section {
  --ranking-accent: color-mix(in srgb, var(--vp-c-brand-1) 70%, #f6b259);
  display: grid;
  gap: 18px;
}

.ranking-section__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.ranking-section__heading-main {
  display: grid;
  gap: 2px;
}

.ranking-section__eyebrow {
  color: var(--ranking-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.ranking-section__meta,
.ranking-section__desc,
.ranking-hero__time,
.ranking-secondary__time,
.ranking-row__time {
  color: var(--vp-c-text-2);
}

.ranking-section__meta {
  margin: 4px 0 0;
  font-size: 13px;
}

.subscribe-pill {
  border: 1px solid color-mix(in srgb, var(--ranking-accent) 34%, transparent);
  border-radius: 999px;
  padding: 8px 14px;
  background: transparent;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.subscribe-pill--tip {
  background: rgba(99, 102, 241, 0.2);
  color: #c7d2fe;
}

.subscribe-pill--danger {
  background: rgba(244, 63, 94, 0.18);
  color: #fecdd3;
}

.ranking-section__desc {
  margin: 0;
}

.ranking-top {
  display: grid;
  gap: 16px;
}

.ranking-hero,
.ranking-secondary__card {
  border: 1px solid var(--vp-c-divider);
  border-radius: 22px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--vp-c-bg-soft) 90%, transparent), color-mix(in srgb, var(--vp-c-bg-elv) 72%, transparent));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.ranking-hero {
  padding: 24px;
}

.ranking-secondary__card {
  padding: 18px;
}

.ranking-hero__body,
.ranking-secondary__body,
.ranking-row__body {
  cursor: pointer;
}

.ranking-badge,
.ranking-row__rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  height: 32px;
  border-radius: 999px;
  background: rgba(255, 175, 64, 0.16);
  color: #d97706;
  font-weight: 700;
}

.ranking-accent--gold {
  background: linear-gradient(135deg, rgba(255, 221, 87, 0.28), rgba(245, 158, 11, 0.18));
  color: #b45309;
}

.ranking-accent--silver {
  background: linear-gradient(135deg, rgba(226, 232, 240, 0.55), rgba(148, 163, 184, 0.22));
  color: #475569;
}

.ranking-accent--bronze {
  background: linear-gradient(135deg, rgba(251, 191, 143, 0.34), rgba(234, 88, 12, 0.18));
  color: #9a3412;
}

.ranking-accent--default {
  background: rgba(255, 175, 64, 0.16);
  color: #d97706;
}

.ranking-hero__title,
.ranking-secondary__title,
.ranking-row__title {
  margin: 12px 0 8px;
}

.ranking-hero__summary,
.ranking-secondary__summary,
.ranking-row__summary {
  margin: 0;
  color: var(--vp-c-text-1);
}

.ranking-secondary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.ranking-row {
  padding: 16px 0;
}

.ranking-media {
  display: block;
  width: 100%;
  height: 180px;
  margin-bottom: 14px;
  border-radius: 16px;
  object-fit: cover;
}

.ranking-media--hero {
  height: 240px;
}

.ranking-media--row {
  width: 72px;
  height: 72px;
  margin: 0;
}

.ranking-media--fallback {
  display: grid;
  place-items: center;
  padding: 16px;
  background:
    linear-gradient(135deg, rgba(255, 210, 122, 0.24), rgba(248, 113, 113, 0.2)),
    var(--vp-c-bg-elv);
  color: var(--vp-c-text-1);
  font-weight: 700;
  text-align: center;
}

.ranking-media--row-fallback {
  width: 72px;
  height: 72px;
  padding: 0;
  margin: 0;
  font-size: 20px;
}

.ranking-rows {
  display: grid;
  gap: 12px;
}

.ranking-row {
  border-bottom: 1px solid color-mix(in srgb, var(--vp-c-divider) 72%, transparent);
}

.ranking-rows--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px 26px;
}

.ranking-rows--two .ranking-row {
  padding-top: 0;
}

.ranking-row__body {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
}

.ranking-row__content {
  min-width: 0;
}

.ranking-card__actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.ranking-card__actions button {
  border: none;
  padding: 0;
  background: transparent;
  color: var(--vp-c-text-2);
  font-size: 13px;
  cursor: pointer;
}

.ranking-card__actions button:hover {
  color: var(--vp-c-brand-1);
}

@media (max-width: 960px) {
  .ranking-section__header,
  .ranking-row__body {
    align-items: flex-start;
    grid-template-columns: 1fr;
  }

  .ranking-secondary {
    grid-template-columns: 1fr;
  }

  .ranking-rows--two {
    grid-template-columns: 1fr;
  }

  .subscribe-pill {
    align-self: flex-start;
  }
}
</style>
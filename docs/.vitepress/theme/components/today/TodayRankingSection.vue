<script setup lang="ts">
import { computed } from "vue";
import {
  extractFirstImageFromSummary,
  extractTextFromSummary,
} from "./summary";
import TodayPreviewImage from "./TodayPreviewImage.vue";
import TodayInlineTranslation from "./TodayInlineTranslation.vue";

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

const getRawTitle = (entity: rssEntity): string => {
  return entity.title === "" ? "Untitled" : entity.title;
};

const getRawSummary = (entity: rssEntity): string => {
  return extractTextFromSummary(entity.summary);
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
        <div class="ranking-section__title-row">
          <h2 class="content-title">{{ title }}</h2>
          <button
            type="button"
            class="subscribe-icon"
            :class="`subscribe-icon--${badgeType}`"
            aria-label="Subscribe feed"
            title="Subscribe feed"
            @click="handleSubscribe"
          >
            <span class="subscribe-icon__glyph" aria-hidden="true"></span>
          </button>
        </div>
        <p class="ranking-section__meta">{{ entries.length }} ranked entries</p>
      </div>
    </header>
    <p v-if="desc" class="ranking-section__desc">{{ desc }}</p>

    <div v-if="topEntries.length > 0" class="ranking-top">
      <article
        v-if="topEntries[0]"
        :id="`item-${sectionKey}-0`"
        class="ranking-hero"
        :class="getRankingAccent(1)"
      >
        <div class="ranking-hero__body">
          <TodayPreviewImage
            v-if="extractFirstImageFromSummary(topEntries[0].summary)"
            :src="extractFirstImageFromSummary(topEntries[0].summary) || undefined"
            :alt="getRawTitle(topEntries[0]) === '' ? 'Untitled ranking preview' : getRawTitle(topEntries[0])"
            variant="ranking-hero"
          />
          <div v-else class="ranking-media ranking-media--fallback">
            {{ getFallbackLabel(1) }}
          </div>
          <span class="ranking-badge" :class="getRankingAccent(1)">#1</span>
          <h3 class="ranking-hero__title">
            <TodayInlineTranslation
              :text="getRawTitle(topEntries[0])"
              :cache-key="`${sectionKey}-0-title`"
              :href="topEntries[0].url"
              link-class="ranking-title-link"
            />
          </h3>
          <p class="ranking-hero__summary">
            <TodayInlineTranslation
              :text="getRawSummary(topEntries[0])"
              :cache-key="`${sectionKey}-0-summary`"
            />
          </p>
          <span class="ranking-hero__time">{{ formatTimestamp(topEntries[0].timestamp) }}</span>
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
          <div class="ranking-secondary__body">
            <TodayPreviewImage
              v-if="extractFirstImageFromSummary(entity.summary)"
              :src="extractFirstImageFromSummary(entity.summary) || undefined"
              :alt="getRawTitle(entity) === '' ? 'Untitled ranking preview' : getRawTitle(entity)"
              variant="ranking-card"
            />
            <div v-else class="ranking-media ranking-media--fallback">
              {{ getFallbackLabel(entityIndex + 2) }}
            </div>
            <span class="ranking-badge" :class="getRankingAccent(entityIndex + 2)">#{{ entityIndex + 2 }}</span>
            <h3 class="ranking-secondary__title">
              <TodayInlineTranslation
                :text="getRawTitle(entity)"
                :cache-key="`${sectionKey}-${entityIndex + 1}-title`"
                :href="entity.url"
                link-class="ranking-title-link"
              />
            </h3>
            <p class="ranking-secondary__summary">
              <TodayInlineTranslation
                :text="getRawSummary(entity)"
                :cache-key="`${sectionKey}-${entityIndex + 1}-summary`"
              />
            </p>
            <span class="ranking-secondary__time">{{ formatTimestamp(entity.timestamp) }}</span>
          </div>
        </article>
      </div>
    </div>

    <div
      v-if="otherEntries.length > 0"
      class="ranking-rows"
    >
      <article
        v-for="(entity, entityIndex) in otherEntries"
        :id="`item-${sectionKey}-${entityIndex + 3}`"
        :key="`${entity.url}-${entityIndex + 3}`"
        class="ranking-row"
      >
        <div class="ranking-row__body">
          <span class="ranking-row__rank">#{{ entityIndex + 4 }}</span>
          <TodayPreviewImage
            v-if="extractFirstImageFromSummary(entity.summary)"
            :src="extractFirstImageFromSummary(entity.summary) || undefined"
            :alt="getRawTitle(entity) === '' ? 'Untitled ranking preview' : getRawTitle(entity)"
            variant="ranking-row"
          />
          <div v-else class="ranking-media ranking-media--fallback ranking-media--row-fallback">
            {{ entityIndex + 4 }}
          </div>
          <div class="ranking-row__content">
            <h3 class="ranking-row__title">
              <TodayInlineTranslation
                :text="getRawTitle(entity)"
                :cache-key="`${sectionKey}-${entityIndex + 3}-title`"
                :href="entity.url"
                link-class="ranking-title-link"
              />
            </h3>
            <p class="ranking-row__summary">
              <TodayInlineTranslation
                :text="getRawSummary(entity)"
                :cache-key="`${sectionKey}-${entityIndex + 3}-summary`"
              />
            </p>
          </div>
          <span class="ranking-row__time">{{ formatTimestamp(entity.timestamp) }}</span>
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

.ranking-section__title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ranking-section__meta,
.ranking-section__desc,
.ranking-hero__time,
.ranking-secondary__time,
.ranking-row__time {
  color: color-mix(in srgb, var(--vp-c-text-2) 84%, var(--ranking-accent) 16%);
  cursor: pointer;
  flex: 0 0 auto;
}

.translate-icon__glyph {
  display: block;
  width: 16px;
  height: 16px;
  background-color: currentColor;
  mask-image: url("../../assets/translate.svg");
  mask-repeat: no-repeat;
  mask-position: center;
  mask-size: contain;
  -webkit-mask-image: url("../../assets/translate.svg");
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  -webkit-mask-size: contain;
  opacity: 0.8;
  transition: opacity 0.18s ease, transform 0.18s ease, background-color 0.18s ease;
}

.translate-icon:hover,
.translate-icon:focus-visible,
.translate-icon--active {
  color: var(--vp-c-brand-1);
}

.translate-icon:hover .translate-icon__glyph,
.translate-icon:focus-visible .translate-icon__glyph,
.translate-icon--active .translate-icon__glyph {
  opacity: 1;
  transform: translateY(-1px);
}

.translate-icon--loading {
  cursor: progress;
}

.translate-icon--loading .translate-icon__glyph {
  opacity: 0.88;
  animation: ranking-translate-spin 0.9s linear infinite;
}

.translate-icon:disabled {
  cursor: progress;
}

@keyframes ranking-translate-spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
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
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--vp-c-bg-soft) 90%, transparent),
      color-mix(in srgb, var(--vp-c-bg-elv) 72%, transparent)
    );
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.ranking-hero {
  padding: 24px;
}

.ranking-secondary__card {
  padding: 18px;
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

.ranking-title-link {
  color: inherit;
  text-decoration: none;
}

.ranking-title-link:hover {
  color: var(--vp-c-brand-1);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 0.16em;
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

.ranking-row__body {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr) auto;
  grid-template-areas: "rank media content time";
  align-items: center;
  gap: 16px;
}

.ranking-row__rank {
  grid-area: rank;
}

.preview-image--ranking-row,
.ranking-media--row-fallback {
  grid-area: media;
}

.ranking-row__content {
  grid-area: content;
  min-width: 0;
}

.ranking-row__time {
  grid-area: time;
  justify-self: end;
}

@media (max-width: 960px) {
  .ranking-section__header {
    align-items: flex-start;
  }

  .ranking-secondary {
    grid-template-columns: 1fr;
  }

  .ranking-row__body {
    grid-template-columns: auto 72px minmax(0, 1fr);
    grid-template-areas:
      "rank media content"
      ". . time";
    align-items: start;
  }

  .ranking-row__time {
    justify-self: start;
  }

  .ranking-section__toolbar {
    justify-content: flex-start;
  }

  .ranking-section__title-row {
    flex-wrap: wrap;
  }
}
</style>
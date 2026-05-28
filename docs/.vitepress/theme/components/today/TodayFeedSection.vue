<script setup lang="ts">
import { computed, ref } from "vue";
import TodayFeedItem from "./TodayFeedItem.vue";
import {
  DEFAULT_AVATAR_URL,
  getFaviconServiceUrl,
  getFaviconUrl,
  getHostnameLabel,
  getRootDomain,
} from "./avatar.ts";

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
  avatarSlots: number;
}>();

const feedIconUrl = new URL("../../assets/feed.svg", import.meta.url).href;

const handleSubscribe = (): void => {
  window.open(props.rss, "_blank");
};

const selectedSource = ref<string | null>(null);

const sourceOptions = computed(() => {
  const uniqueSources = new Map<string, {
    key: string;
    label: string;
    src: string;
    count: number;
    alt: string;
  }>();

  props.entries.forEach((entry) => {
    const sourceKey = getRootDomain(entry.url) ?? entry.url;
    const existing = uniqueSources.get(sourceKey);

    if (existing) {
      existing.count += 1;
      return;
    }

    const label = getHostnameLabel(entry.url);
    uniqueSources.set(sourceKey, {
      key: sourceKey,
      label,
      src: getFaviconUrl(entry.url),
      count: 1,
      alt: `${label} favicon`,
    });
  });

  return Array.from(uniqueSources.values());
});

const filteredEntries = computed(() => {
  if (!selectedSource.value) {
    return props.entries;
  }

  return props.entries.filter((entry) => {
    return (getRootDomain(entry.url) ?? entry.url) === selectedSource.value;
  });
});

const displayedEntryCount = computed(() => {
  if (!selectedSource.value) {
    return `${props.entries.length} entries today`;
  }

  return `${filteredEntries.value.length} / ${props.entries.length} entries`;
});

const toggleSourceFilter = (sourceKey: string): void => {
  selectedSource.value = selectedSource.value === sourceKey ? null : sourceKey;
};

const handleAvatarError = (event: Event, entryUrl: string): void => {
  const target = event.target as HTMLImageElement;

  if (target.dataset.faviconFallback !== "service") {
    target.dataset.faviconFallback = "service";
    target.src = getFaviconServiceUrl(entryUrl);
    return;
  }

  target.onerror = null;
  target.src = DEFAULT_AVATAR_URL;
};

</script>

<template>
  <section class="feed-section">
    <header
      v-if="entries.length > 0"
      :id="`section-${sectionKey}`"
      class="feed-section__header"
    >
      <div class="feed-section__heading">
        <div class="feed-section__heading-main">
          <span class="feed-section__eyebrow">Moments Stream</span>
          <div class="feed-section__title-row">
            <h2 class="content-title">{{ title }}</h2>
            <button
              type="button"
              class="subscribe-icon"
              :class="`subscribe-icon--${badgeType}`"
              aria-label="Subscribe feed"
              title="Subscribe feed"
              @click="handleSubscribe"
            >
              <img :src="feedIconUrl" alt="" />
            </button>
          </div>
          <p class="feed-section__meta">{{ displayedEntryCount }}</p>
        </div>
      </div>
      <div class="feed-section__toolbar">
        <span class="feed-section__sources-label">Sources</span>
        <div class="feed-section__sources">
          <div class="feed-section__avatars" aria-label="Feed sources filter">
            <button
              v-for="source in sourceOptions"
              :key="source.key"
              type="button"
              class="feed-section__source"
              :class="{ 'feed-section__source--active': selectedSource === source.key }"
              :title="`${source.label} · ${source.count}`"
              @click="toggleSourceFilter(source.key)"
            >
              <img
                class="feed-section__avatar"
                :src="source.src"
                :alt="source.alt"
                loading="lazy"
                @error="handleAvatarError($event, source.key)"
              />
              <span class="feed-section__source-label">{{ source.label }}</span>
              <span class="feed-section__source-count">{{ source.count }}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
    <p v-if="desc" class="feed-section__desc">{{ desc }}</p>

    <div class="feed-list">
      <TodayFeedItem
        v-for="(entity, entityIndex) in filteredEntries"
        :key="`${entity.url}-${entityIndex}`"
        :section-key="sectionKey"
        :entity="entity"
        :entity-index="entityIndex"
      />
    </div>
  </section>
</template>

<style scoped>
.feed-section {
  --feed-accent: color-mix(in srgb, var(--vp-c-brand-1) 72%, #8bd18f);
  display: grid;
  gap: 14px;
}

.feed-list {
  display: grid;
  gap: 0;
}

.feed-section__header {
  display: grid;
  gap: 10px;
  margin-bottom: 8px;
}

.feed-section__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.feed-section__heading-main {
  display: grid;
  gap: 2px;
}

.feed-section__title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.feed-section__eyebrow {
  color: var(--feed-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.content-title {
  margin: 0;
  font-size: clamp(1.9rem, 2.4vw, 2.35rem);
  line-height: 0.96;
}

.feed-section__meta {
  margin: 2px 0 0;
  color: var(--vp-c-text-2);
  font-size: 13px;
}

.feed-section__toolbar {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 12px;
}

.feed-section__sources {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.feed-section__avatars {
  display: flex;
  align-items: center;
  gap: 0;
  min-width: 0;
  max-width: 100%;
  overflow-x: auto;
  padding: 2px 0 2px 4px;
  scrollbar-width: none;
}

.feed-section__avatars::-webkit-scrollbar {
  display: none;
}

.feed-section__sources-label {
  color: var(--vp-c-text-2);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.feed-section__source {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
  margin-left: -12px;
  border: 1px solid color-mix(in srgb, var(--vp-c-divider) 70%, transparent);
  border-radius: 999px;
  padding: 4px 10px 4px 4px;
  background: color-mix(in srgb, var(--vp-c-bg-soft) 92%, transparent);
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition:
    margin 0.2s ease,
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease,
    color 0.2s ease;
}

.feed-section__avatars:hover .feed-section__source,
.feed-section__avatars:focus-within .feed-section__source,
.feed-section__source--active {
  margin-left: 0;
}

.feed-section__source:hover,
.feed-section__source:focus-visible,
.feed-section__source--active {
  border-color: color-mix(in srgb, var(--feed-accent) 48%, transparent);
  background: color-mix(in srgb, var(--feed-accent) 18%, var(--vp-c-bg-elv));
  color: var(--vp-c-text-1);
  transform: translateY(-1px);
}

.feed-section__avatar {
  display: block;
  width: 40px;
  height: 40px;
  overflow: hidden;
  border-radius: 999px;
  border: 1px dashed color-mix(in srgb, var(--vp-c-brand-1) 45%, transparent);
  background: color-mix(in srgb, var(--vp-c-bg-soft) 88%, transparent);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
  object-fit: cover;
}

.feed-section__source-label {
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.feed-section__source-count {
  min-width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: color-mix(in srgb, var(--vp-c-brand-1) 16%, transparent);
  font-size: 11px;
  font-weight: 700;
}

.feed-section__desc {
  margin: 0 0 16px;
  color: var(--vp-c-text-2);
}

.subscribe-icon {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: auto;
  height: auto;
  border: none;
  padding: 0;
  background: transparent;
  line-height: 1;
  cursor: pointer;
}

.subscribe-icon img {
  display: block;
  width: 17px;
  height: 17px;
  opacity: 0.78;
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.subscribe-icon:hover img,
.subscribe-icon:focus-visible img {
  opacity: 1;
  transform: translateY(-1px);
}

@media (max-width: 640px) {
  .feed-section__heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .feed-section__toolbar {
    grid-template-columns: 1fr;
  }

  .feed-section__sources {
    width: 100%;
  }

  .feed-section__title-row {
    flex-wrap: wrap;
  }

  .feed-section__source {
    margin-left: -16px;
  }
}
</style>
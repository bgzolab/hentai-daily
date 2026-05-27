<script setup lang="ts">
import { computed } from "vue";
import {
  DEFAULT_AVATAR_URL,
  getFaviconUrl,
  getHostnameLabel,
} from "./avatar.ts";
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
  entity: rssEntity;
  entityIndex: number;
}>();

const formatTimestamp = (timestamp: number): string => {
  return new Date(timestamp * 1000).toLocaleString();
};

const previewImage = computed(() => {
  return extractFirstImageFromSummary(props.entity.summary);
});

const summaryText = computed(() => {
  return extractTextFromSummary(props.entity.summary);
});

const streamLabel = computed(() => {
  return props.sectionKey === "News" ? "Moments / News" : "Moments / Resources";
});

const sourceLabel = computed(() => {
  return getHostnameLabel(props.entity.url);
});

const avatarUrl = computed(() => {
  return getFaviconUrl(props.entity.url);
});

const handleAvatarError = (event: Event): void => {
  const target = event.target as HTMLImageElement;
  target.onerror = null;
  target.src = DEFAULT_AVATAR_URL;
};
</script>

<template>
  <article :id="`item-${sectionKey}-${entityIndex}`" class="feed-item">
    <div class="feed-item__rail">
      <img
        class="feed-item__avatar"
        :src="avatarUrl"
        :alt="entity.title === '' ? 'Untitled favicon' : `${entity.title} favicon`"
        loading="lazy"
        @error="handleAvatarError"
      />
    </div>
    <div class="feed-item__content">
      <div class="feed-item__meta">
        <div class="feed-item__channel">
          <span class="feed-item__source">{{ streamLabel }}</span>
          <span class="feed-item__site">{{ sourceLabel }}</span>
          <span class="feed-item__time">{{ formatTimestamp(entity.timestamp) }}</span>
        </div>
        <h3 class="feed-item__title">
          <a
            class="feed-item__title-link"
            :href="entity.url"
            target="_blank"
            rel="noreferrer"
          >
            {{ entity.title === "" ? "Untitled" : entity.title }}
          </a>
        </h3>
      </div>
      <p
        class="feed-item__summary"
        :class="{ 'feed-item__summary--clamped': !previewImage }"
      >
        {{ summaryText || "No summary available." }}
      </p>
      <img
        v-if="previewImage"
        class="feed-item__image"
        :src="previewImage"
        :alt="entity.title === '' ? 'Untitled preview image' : entity.title"
      />
    </div>
  </article>
</template>

<style scoped>
.feed-item {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr);
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid color-mix(in srgb, var(--vp-c-divider) 70%, transparent);
  background: transparent;
}

.feed-item__rail {
  display: flex;
  justify-content: flex-start;
  padding-top: 2px;
}

.feed-item__avatar {
  display: block;
  width: 48px;
  height: 48px;
  overflow: hidden;
  border-radius: 999px;
  border: 1px dashed color-mix(in srgb, var(--vp-c-brand-1) 45%, transparent);
  background: color-mix(in srgb, var(--vp-c-bg-soft) 88%, transparent);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.3);
  object-fit: cover;
}

.feed-item__content {
  min-width: 0;
  display: grid;
  gap: 10px;
}

.feed-item__meta {
  display: grid;
  gap: 6px;
}

.feed-item__channel {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.feed-item__source {
  color: var(--vp-c-text-1);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.feed-item__site {
  color: var(--vp-c-text-2);
  font-size: 12px;
  letter-spacing: 0.03em;
  text-transform: lowercase;
}

.feed-item__title {
  margin: 0;
  font-size: 1.12rem;
  line-height: 1.4;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.feed-item__title-link {
  color: inherit;
  text-decoration: none;
}

.feed-item__title-link:hover {
  color: var(--vp-c-brand-1);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 0.16em;
}

.feed-item__time {
  color: var(--vp-c-text-2);
  font-size: 12px;
}

.feed-item__summary {
  margin: 0;
  max-width: 58ch;
  color: var(--vp-c-text-2);
  line-height: 1.75;
}

.feed-item__summary--clamped {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
}

.feed-item__image {
  display: block;
  width: min(100%, 520px);
  max-height: 220px;
  margin: 0;
  border-radius: 16px;
  box-shadow: 0 20px 36px -28px rgba(0, 0, 0, 0.45);
  object-fit: cover;
}

@media (max-width: 640px) {
  .feed-item {
    grid-template-columns: 44px minmax(0, 1fr);
    padding: 18px 0;
  }

  .feed-item__rail {
    justify-content: flex-start;
  }

  .feed-item__summary,
  .feed-item__image {
    max-width: 100%;
    width: 100%;
  }
}
</style>
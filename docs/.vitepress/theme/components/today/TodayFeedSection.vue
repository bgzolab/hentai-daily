<script setup lang="ts">
import { computed } from "vue";
import TodayFeedItem from "./TodayFeedItem.vue";
import { DEFAULT_AVATAR_URL, getFaviconUrl } from "./avatar.ts";

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

const emit = defineEmits<{
  open: [url: string];
  copy: [url: string];
}>();

const handleSubscribe = (): void => {
  window.open(props.rss, "_blank");
};

const headerAvatars = computed(() => {
  return Array.from({ length: props.avatarSlots }, (_, index) => {
    const entry = props.entries[index];

    return {
      key: `${props.sectionKey}-${index}`,
      src: entry ? getFaviconUrl(entry.url) : DEFAULT_AVATAR_URL,
      alt: entry ? `${entry.title || props.title} favicon` : `${props.title} default avatar`,
    };
  });
});

const handleAvatarError = (event: Event): void => {
  const target = event.target as HTMLImageElement;
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
          <h2 class="content-title">{{ title }}</h2>
          <p class="feed-section__meta">{{ entries.length }} entries today</p>
        </div>
        <button
          type="button"
          class="subscribe-pill"
          :class="`subscribe-pill--${badgeType}`"
          @click="handleSubscribe"
        >
          subscribe
        </button>
      </div>
      <div class="feed-section__avatars" aria-label="Reserved avatar placeholders">
        <img
          v-for="avatar in headerAvatars"
          :key="avatar.key"
          class="feed-section__avatar"
          :src="avatar.src"
          :alt="avatar.alt"
          loading="lazy"
          @error="handleAvatarError"
        />
      </div>
    </header>
    <p v-if="desc" class="feed-section__desc">{{ desc }}</p>

    <div class="feed-list">
      <TodayFeedItem
        v-for="(entity, entityIndex) in entries"
        :key="`${entity.url}-${entityIndex}`"
        :section-key="sectionKey"
        :entity="entity"
        :entity-index="entityIndex"
        @open="emit('open', $event)"
        @copy="emit('copy', $event)"
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

.feed-section__avatars {
  display: flex;
  align-items: center;
  gap: 0;
  padding-left: 4px;
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
  margin-left: -10px;
  object-fit: cover;
}

.feed-section__desc {
  margin: 0 0 16px;
  color: var(--vp-c-text-2);
}

.subscribe-pill {
  border: 1px solid color-mix(in srgb, var(--feed-accent) 38%, transparent);
  border-radius: 999px;
  padding: 7px 14px;
  background: transparent;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  cursor: pointer;
}

.subscribe-pill--tip {
  color: color-mix(in srgb, var(--feed-accent) 72%, white);
}

.subscribe-pill--danger {
  color: #fecdd3;
}

@media (max-width: 640px) {
  .feed-section__heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .subscribe-pill {
    align-self: flex-start;
  }
}
</style>
<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";

const props = defineProps<{
  src: string;
  alt: string;
  variant: "feed" | "ranking-hero" | "ranking-card" | "ranking-row";
}>();

const isOpen = ref(false);

const previewLabel = computed(() => {
  return props.alt || "Preview image";
});

const openPreview = (): void => {
  isOpen.value = true;
};

const closePreview = (): void => {
  isOpen.value = false;
};

const handleKeydown = (event: KeyboardEvent): void => {
  if (event.key === "Escape") {
    closePreview();
  }
};

if (typeof window !== "undefined") {
  window.addEventListener("keydown", handleKeydown);
}

onBeforeUnmount(() => {
  if (typeof window !== "undefined") {
    window.removeEventListener("keydown", handleKeydown);
  }
});
</script>

<template>
  <button
    type="button"
    class="preview-image"
    :class="`preview-image--${variant}`"
    :aria-label="`Preview ${previewLabel}`"
    @click="openPreview"
  >
    <img class="preview-image__img" :src="src" :alt="alt" loading="lazy" />
    <span class="preview-image__hint">Preview</span>
  </button>

  <Teleport to="body">
    <div
      v-if="isOpen"
      class="preview-lightbox"
      role="dialog"
      aria-modal="true"
      :aria-label="previewLabel"
      @click="closePreview"
    >
      <button
        type="button"
        class="preview-lightbox__close"
        aria-label="Close preview"
        @click.stop="closePreview"
      >
        Close
      </button>
      <img
        class="preview-lightbox__image"
        :src="src"
        :alt="alt"
        @click.stop
      />
    </div>
  </Teleport>
</template>

<style scoped>
.preview-image {
  position: relative;
  display: block;
  overflow: hidden;
  border: none;
  padding: 0;
  background: transparent;
  text-align: left;
  cursor: zoom-in;
}

.preview-image__img {
  display: block;
  width: 100%;
  border-radius: 16px;
  object-fit: cover;
  transition: transform 0.22s ease, filter 0.22s ease;
}

.preview-image:hover .preview-image__img,
.preview-image:focus-visible .preview-image__img {
  transform: scale(1.02);
  filter: saturate(1.05);
}

.preview-image__hint {
  position: absolute;
  right: 12px;
  bottom: 12px;
  border-radius: 999px;
  padding: 4px 10px;
  background: rgba(12, 18, 28, 0.72);
  color: white;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  opacity: 0;
  transform: translateY(4px);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.preview-image:hover .preview-image__hint,
.preview-image:focus-visible .preview-image__hint {
  opacity: 1;
  transform: translateY(0);
}

.preview-image--feed {
  width: min(100%, 520px);
}

.preview-image--feed .preview-image__img {
  max-height: 220px;
  box-shadow: 0 20px 36px -28px rgba(0, 0, 0, 0.45);
}

.preview-image--ranking-hero,
.preview-image--ranking-card {
  width: 100%;
  margin-bottom: 14px;
}

.preview-image--ranking-hero .preview-image__img {
  height: 240px;
}

.preview-image--ranking-card .preview-image__img {
  height: 180px;
}

.preview-image--ranking-row {
  width: 72px;
  height: 72px;
}

.preview-image--ranking-row .preview-image__img {
  width: 72px;
  height: 72px;
}

.preview-image--ranking-row .preview-image__hint {
  right: 6px;
  bottom: 6px;
  padding: 2px 6px;
  font-size: 9px;
}

.preview-lightbox {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(6, 10, 18, 0.82);
  backdrop-filter: blur(12px);
  z-index: 999;
}

.preview-lightbox__close {
  position: absolute;
  top: 18px;
  right: 18px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.08);
  color: white;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.preview-lightbox__image {
  max-width: min(1100px, 92vw);
  max-height: 88vh;
  border-radius: 20px;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.48);
}

@media (prefers-reduced-motion: reduce) {
  .preview-image__img,
  .preview-image__hint {
    transition: none;
  }
}

@media (max-width: 640px) {
  .preview-image--feed {
    width: 100%;
  }
}
</style>
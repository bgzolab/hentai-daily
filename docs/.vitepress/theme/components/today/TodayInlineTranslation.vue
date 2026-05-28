<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { canTranslateToChinese, translateToChinese } from "./translation";

const props = withDefaults(defineProps<{
  text: string;
  cacheKey: string;
  href?: string;
  linkClass?: string;
}>(), {
  href: undefined,
  linkClass: "",
});

const translatedText = ref("");
const showTranslatedText = ref(false);
const isTranslating = ref(false);

const normalizedText = computed(() => {
  return props.text.trim();
});

const shouldShowTranslateAction = computed(() => {
  return canTranslateToChinese(normalizedText.value);
});

const displayText = computed(() => {
  if (!showTranslatedText.value) {
    return props.text;
  }

  return translatedText.value || props.text;
});

const actionLabel = computed(() => {
  if (isTranslating.value) {
    return "翻译中...";
  }

  return showTranslatedText.value ? "隐藏中文" : "翻译成中文";
});

watch(
  () => [props.text, props.cacheKey],
  () => {
    translatedText.value = "";
    showTranslatedText.value = false;
    isTranslating.value = false;
  },
  { immediate: true },
);

const handleToggleTranslation = async (): Promise<void> => {
  if (!shouldShowTranslateAction.value) {
    return;
  }

  if (showTranslatedText.value) {
    showTranslatedText.value = false;
    return;
  }

  showTranslatedText.value = true;

  if (translatedText.value !== "") {
    return;
  }

  isTranslating.value = true;
  translatedText.value = await translateToChinese(props.text);
  isTranslating.value = false;
};
</script>

<template>
  <span class="inline-translation">
    <a
      v-if="href"
      :href="href"
      target="_blank"
      rel="noreferrer"
      :class="linkClass"
    >
      {{ displayText }}
    </a>
    <span v-else>{{ displayText }}</span>
    <button
      v-if="shouldShowTranslateAction"
      type="button"
      class="translate-icon"
      :class="{
        'translate-icon--active': showTranslatedText,
        'translate-icon--loading': isTranslating,
      }"
      :disabled="isTranslating"
      :title="actionLabel"
      :aria-label="actionLabel"
      @click="handleToggleTranslation"
    >
      <span class="translate-icon__glyph" aria-hidden="true"></span>
    </button>
  </span>
</template>

<style scoped>
.inline-translation {
  display: inline;
}

.translate-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.05em;
  height: 1.05em;
  margin-left: 0.34em;
  border: none;
  padding: 0;
  background: transparent;
  color: color-mix(in srgb, var(--vp-c-text-2) 84%, var(--vp-c-brand-1) 16%);
  cursor: pointer;
  vertical-align: -0.08em;
}

.translate-icon__glyph {
  display: block;
  width: 100%;
  height: 100%;
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
}

.translate-icon--loading {
  cursor: progress;
}

.translate-icon--loading .translate-icon__glyph {
  animation: inline-translate-spin 0.9s linear infinite;
  opacity: 0.9;
}

.translate-icon:disabled {
  cursor: progress;
}

@keyframes inline-translate-spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
</style>
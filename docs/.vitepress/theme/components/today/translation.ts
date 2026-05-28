const TRANSLATE_API_URL = "https://api.mymemory.translated.net/get";
const TRANSLATE_STORAGE_KEY = "hentai-daily-ranking-translation-cache-v1";
const MAX_QUERY_BYTES = 480;
const CHINESE_ONLY_RE = /^[\u4e00-\u9fff0-9\s，。！？、；：“”‘’（）《》【】—…,.!?:;'"\-_/]+$/;
const JAPANESE_KANA_RE = /[\u3040-\u30ff\u31f0-\u31ff\uff66-\uff9f]/;

const translationCache = new Map<string, string>();
const pendingTranslations = new Map<string, Promise<string>>();

let cacheLoaded = false;

const normalizeText = (text: string): string => {
  return text.replace(/\s+/g, " ").trim();
};

export const canTranslateToChinese = (text: string): boolean => {
  const normalized = normalizeText(text);
  if (normalized === "") {
    return false;
  }

  if (JAPANESE_KANA_RE.test(normalized)) {
    return true;
  }

  return !CHINESE_ONLY_RE.test(normalized);
};

const trimToByteLimit = (text: string, maxBytes = MAX_QUERY_BYTES): string => {
  const normalized = normalizeText(text);
  const encoder = new TextEncoder();

  if (encoder.encode(normalized).length <= maxBytes) {
    return normalized;
  }

  let end = normalized.length;
  while (end > 0 && encoder.encode(normalized.slice(0, end)).length > maxBytes) {
    end -= 1;
  }

  return normalized.slice(0, end).trim();
};

const loadCacheFromStorage = (): void => {
  if (cacheLoaded || typeof window === "undefined") {
    return;
  }

  cacheLoaded = true;

  try {
    const raw = window.sessionStorage.getItem(TRANSLATE_STORAGE_KEY);
    if (!raw) {
      return;
    }

    const parsed = JSON.parse(raw) as Record<string, string>;
    Object.entries(parsed).forEach(([key, value]) => {
      if (typeof value === "string") {
        translationCache.set(key, value);
      }
    });
  } catch (error) {
    console.warn("加载翻译缓存失败", error);
  }
};

const persistCacheToStorage = (): void => {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.sessionStorage.setItem(
      TRANSLATE_STORAGE_KEY,
      JSON.stringify(Object.fromEntries(translationCache.entries())),
    );
  } catch (error) {
    console.warn("写入翻译缓存失败", error);
  }
};

const requestTranslation = async (text: string): Promise<string> => {
  const query = trimToByteLimit(text);
  if (query === "") {
    return "";
  }

  const url = new URL(TRANSLATE_API_URL);
  url.searchParams.set("q", query);
  url.searchParams.set("langpair", "ja|zh-CN");
  url.searchParams.set("mt", "1");

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Translate request failed: ${response.status}`);
  }

  const payload = (await response.json()) as {
    responseData?: {
      translatedText?: string;
    };
  };

  return normalizeText(payload.responseData?.translatedText ?? "") || text;
};

export const translateToChinese = async (text: string): Promise<string> => {
  const normalized = normalizeText(text);
  if (!canTranslateToChinese(normalized)) {
    return normalized;
  }

  if (typeof window === "undefined") {
    return normalized;
  }

  loadCacheFromStorage();

  const cached = translationCache.get(normalized);
  if (cached) {
    return cached;
  }

  const pending = pendingTranslations.get(normalized);
  if (pending) {
    return pending;
  }

  const task = requestTranslation(normalized)
    .catch((error) => {
      console.warn("翻译请求失败，回退原文", error);
      return normalized;
    })
    .then((translated) => {
      translationCache.set(normalized, translated);
      pendingTranslations.delete(normalized);
      persistCacheToStorage();
      return translated;
    });

  pendingTranslations.set(normalized, task);
  return task;
};
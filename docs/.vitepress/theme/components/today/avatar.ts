export const DEFAULT_AVATAR_URL = new URL(
  "../../assets/default.jpg",
  import.meta.url,
).href;

const normalizeUrl = (url: string): string | null => {
  try {
    if (url.startsWith("//")) {
      return `https:${url}`;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      return `https://${url}`;
    }

    return url;
  } catch {
    return null;
  }
};

export const getRootDomain = (url: string): string | null => {
  try {
    const normalizedUrl = normalizeUrl(url);
    if (!normalizedUrl) {
      return null;
    }

    return new URL(normalizedUrl).origin;
  } catch {
    return null;
  }
};

export const getFaviconUrl = (url: string): string => {
  const origin = getRootDomain(url);
  return origin ? `${origin}/favicon.ico` : DEFAULT_AVATAR_URL;
};
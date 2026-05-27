export const extractFirstImageFromSummary = (
  summary: string,
): string | null => {
  const match = summary.match(/<img[^>]+src\s*=\s*["']([^"']+)["']/i);
  return match?.[1] ?? null;
};

export const extractTextFromSummary = (summary: string): string => {
  return summary
    .replace(/<img[^>]*>/gi, " ")
    .replace(/<br\s*\/?>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/\s+/g, " ")
    .trim();
};
export interface RecentConsultation {
  id: string;
  query: string;
  snippet?: string;
  timestamp: number;
}

const STORAGE_KEY = "ebis_recent_consultations";
const MAX_ITEMS = 6;

export function getRecentConsultations(): RecentConsultation[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed.slice(0, MAX_ITEMS);
    }
  } catch (e) {
    console.warn("Could not read recent consultations from localStorage", e);
  }
  return [];
}

export function saveRecentConsultation(query: string, snippet?: string): void {
  if (typeof window === "undefined" || !query || !query.trim()) return;
  try {
    const current = getRecentConsultations();
    const cleanQuery = query.trim();
    // Remove duplicate of the same query if already present
    const filtered = current.filter((item) => item.query.toLowerCase() !== cleanQuery.toLowerCase());
    const newItem: RecentConsultation = {
      id: "consultation-" + Date.now(),
      query: cleanQuery,
      snippet: snippet ? snippet.slice(0, 140) : undefined,
      timestamp: Date.now(),
    };
    const updated = [newItem, ...filtered].slice(0, MAX_ITEMS);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    // Trigger custom window event so open sidebar/components update reactively
    window.dispatchEvent(new Event("ebis_consultations_updated"));
  } catch (e) {
    console.warn("Could not save recent consultation to localStorage", e);
  }
}

export function clearRecentConsultations(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(STORAGE_KEY);
    window.dispatchEvent(new Event("ebis_consultations_updated"));
  } catch (e) {
    console.warn("Could not clear recent consultations", e);
  }
}

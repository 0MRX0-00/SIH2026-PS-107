import rawData from "@/data/laboratories.json";
import {
  LaboratoryItem,
  LaboratorySearchResponse,
  LaboratoryStats
} from "./api";
import {
  localizeLabName,
  localizeCity,
  localizeState,
  localizeTestingScope
} from "./localizeLab";

const allLabs: LaboratoryItem[] = (rawData as any).laboratories || [];

export function getFallbackLaboratoryStats(): LaboratoryStats {
  const recognized_count = allLabs.filter(
    (l) => l.recognition_type === "BIS_RECOGNIZED"
  ).length;
  const empaneled_count = allLabs.filter(
    (l) => l.recognition_type === "BIS_EMPANELLED"
  ).length;
  const institutional_count = allLabs.filter((l) =>
    ["BIS_CENTRAL", "BIS_BRANCH"].includes(l.recognition_type)
  ).length;

  const stateSet = new Set<string>();
  allLabs.forEach((l) => {
    if (l.state && l.state !== "Unknown") {
      stateSet.add(l.state);
    }
  });

  const states = Array.from(stateSet).sort();

  return {
    total_laboratories: allLabs.length,
    recognized_count,
    empaneled_count,
    institutional_count,
    active_count: allLabs.filter((l) => l.status === "ACTIVE").length,
    expired_count: allLabs.filter((l) => l.status === "EXPIRED").length,
    total_states: states.length,
    states,
    last_imported_at: "2026-10-10",
  };
}

export function searchFallbackLaboratories(params: {
  query?: string;
  lab_code?: string;
  city?: string;
  district?: string;
  state?: string;
  standard_number?: string;
  recognition_type?: string;
  status?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: string;
  language?: string;
}): LaboratorySearchResponse {
  const q_lower = (params.query || "").trim().toLowerCase();
  const code_filter = (params.lab_code || "").trim().toLowerCase();
  const city_lower = (params.city || "").trim().toLowerCase();
  const district_lower = (params.district || "").trim().toLowerCase();
  const state_lower = (params.state || "").trim().toLowerCase();
  const std_lower = (params.standard_number || "").trim().toLowerCase();
  const recog_lower = (params.recognition_type || "").trim().toLowerCase();
  const status_lower = (params.status || "").trim().toLowerCase();

  const product_std_map: Record<string, string> = {
    fan: "17803",
    "ceiling fan": "17803",
    "electric fan": "17803",
    plug: "1293",
    socket: "1293",
    water: "14543",
    "mineral water": "13428",
    bottle: "14543",
    "drinking water": "14543",
    laptop: "13252",
    computer: "13252",
    electronics: "13252",
    "it equipment": "13252",
    led: "15885",
    lighting: "15885",
    steel: "1786",
    tmt: "1786",
    iron: "2062",
    cement: "269",
    concrete: "456",
    cable: "694",
    wire: "694",
    battery: "16046",
    cell: "16046",
    solar: "16221",
    photovoltaic: "16221",
    toy: "9873",
    footwear: "15844",
    shoe: "15844",
    switch: "3854",
    pump: "9079",
    appliance: "302",
  };

  let mapped_std: string | null = null;
  if (q_lower) {
    for (const [k, v] of Object.entries(product_std_map)) {
      if (q_lower.includes(k)) {
        mapped_std = v;
        break;
      }
    }
  }

  const std_num_match = std_lower.match(/\b\d{3,6}\b/);
  const std_base_num = std_num_match ? std_num_match[0] : null;

  const results: LaboratoryItem[] = [];

  for (const lab of allLabs) {
    // 1. Lab Code filter
    if (code_filter) {
      const c = (lab.lab_code || "").toLowerCase();
      if (!c.includes(code_filter)) continue;
    }

    // 2. City filter
    if (city_lower) {
      const c = (lab.city || "").toLowerCase();
      if (!c.includes(city_lower)) continue;
    }

    // 3. District filter
    if (district_lower) {
      const d = (lab.district || "").toLowerCase();
      if (!d.includes(district_lower)) continue;
    }

    // 4. State filter
    if (state_lower && state_lower !== "all states") {
      const s = (lab.state || "").toLowerCase();
      if (!s.includes(state_lower)) continue;
    }

    // 5. Recognition Type filter
    if (recog_lower && recog_lower !== "all") {
      const r = (lab.recognition_type || "").toLowerCase();
      if (!r.includes(recog_lower)) continue;
    }

    // 6. Status filter
    if (status_lower && status_lower !== "all") {
      const st = (lab.status || "ACTIVE").toLowerCase();
      if (st !== status_lower) continue;
    }

    // 7. Standard number filter
    if (std_lower) {
      let std_match = false;
      const accredited = lab.accredited_standards || [];
      for (const acc of accredited) {
        const acc_lower = acc.toLowerCase();
        if (acc_lower.includes(std_lower) || std_lower.includes(acc_lower)) {
          std_match = true;
          break;
        }
        if (std_base_num && acc_lower.includes(std_base_num)) {
          std_match = true;
          break;
        }
      }

      if (!std_match) {
        const scope_text = `${lab.testing_scope_summary || ""} ${lab.lab_name || ""}`.toLowerCase();
        if (
          scope_text.includes(std_lower) ||
          (std_base_num && scope_text.includes(std_base_num))
        ) {
          std_match = true;
        }
      }

      if (!std_match) continue;
    }

    // 8. Keyword Query search
    if (q_lower) {
      const contactStr = JSON.stringify(lab.contact_details || {}).toLowerCase();
      const accreditedStr = (lab.accredited_standards || []).join(" ").toLowerCase();
      const searchable = `${lab.lab_name || ""} ${lab.lab_code || ""} ${lab.city || ""} ${lab.district || ""} ${lab.state || ""} ${lab.address || ""} ${contactStr} ${lab.testing_scope_summary || ""} ${accreditedStr}`.toLowerCase();

      let has_match = searchable.includes(q_lower);
      if (!has_match && mapped_std) {
        has_match =
          (lab.accredited_standards || []).some((s) => s.toLowerCase().includes(mapped_std!)) ||
          searchable.includes(mapped_std);
      }

      if (!has_match) {
        const stopWords = new Set([
          "which", "what", "where", "test", "my", "product", "laboratory",
          "laboratories", "lab", "labs", "can", "the", "and", "for", "find"
        ]);
        const tokens = q_lower.split(/\s+/).filter((t) => t.length > 2 && !stopWords.has(t));
        if (tokens.length > 0) {
          has_match = tokens.some((t) => searchable.includes(t));
        }
      }

      if (!has_match) continue;
    }

    results.push(lab);
  }

  // Sorting
  const sortBy = (params.sort_by || "name").toLowerCase();
  const reverse = (params.sort_order || "asc").toLowerCase() === "desc";

  results.sort((a, b) => {
    let cmp = 0;
    if (sortBy === "code") {
      cmp = (a.lab_code || "").localeCompare(b.lab_code || "");
    } else if (sortBy === "state") {
      cmp = (a.state || "").localeCompare(b.state || "") || (a.city || "").localeCompare(b.city || "");
    } else if (sortBy === "city") {
      cmp = (a.city || "").localeCompare(b.city || "");
    } else if (sortBy === "validity") {
      cmp = (a.validity_date || "").localeCompare(b.validity_date || "");
    } else {
      cmp = (a.lab_name || "").localeCompare(b.lab_name || "");
    }
    return reverse ? -cmp : cmp;
  });

  const page = Math.max(1, params.page || 1);
  const pageSize = Math.max(1, params.page_size || 20);
  const total_count = results.length;
  const total_pages = Math.max(1, Math.ceil(total_count / pageSize));
  const start_idx = (page - 1) * pageSize;
  const paginated_items = results.slice(start_idx, start_idx + pageSize);

  const lang = params.language || "en";
  const localized_items = paginated_items.map((lab) => {
    if (lang === "hi" || lang === "ta") {
      return {
        ...lab,
        lab_name: localizeLabName(lab.lab_name, lang),
        city: localizeCity(lab.city, lang),
        district: lab.district ? localizeCity(lab.district, lang) : lab.district,
        state: localizeState(lab.state, lang),
        testing_scope_summary: localizeTestingScope(lab.testing_scope_summary, lang),
      };
    }
    return lab;
  });

  return {
    total_count,
    page,
    page_size: pageSize,
    total_pages,
    has_next: page < total_pages,
    has_prev: page > 1,
    laboratories: localized_items,
  };
}

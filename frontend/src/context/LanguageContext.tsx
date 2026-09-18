"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import en from "@/locales/en.json";
import hi from "@/locales/hi.json";
import ta from "@/locales/ta.json";

export type LanguageCode = "en" | "hi" | "ta";

interface LanguageContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  t: (keyPath: string, fallback?: string) => string;
}

const dictionaries: Record<LanguageCode, any> = { en, hi, ta };

const LanguageContext = createContext<LanguageContextType>({
  language: "en",
  setLanguage: () => {},
  t: (keyPath: string, fallback?: string) => fallback || keyPath,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<LanguageCode>("en");

  useEffect(() => {
    const saved = localStorage.getItem("ebis_language_preference") as LanguageCode;
    if (saved && ["en", "hi", "ta"].includes(saved)) {
      setLanguageState(saved);
    }
  }, []);

  const setLanguage = (lang: LanguageCode) => {
    setLanguageState(lang);
    try {
      localStorage.setItem("ebis_language_preference", lang);
    } catch (e) {
      console.warn("Could not save language preference to localStorage", e);
    }
  };

  const t = (keyPath: string, fallback?: string): string => {
    const dict = dictionaries[language] || dictionaries.en;
    const keys = keyPath.split(".");
    let current: any = dict;

    for (const key of keys) {
      if (current && typeof current === "object" && key in current) {
        current = current[key];
      } else {
        // Fallback to English dictionary if key is missing in active locale
        let enCurrent: any = dictionaries.en;
        for (const enKey of keys) {
          if (enCurrent && typeof enCurrent === "object" && enKey in enCurrent) {
            enCurrent = enCurrent[enKey];
          } else {
            return fallback || keyPath;
          }
        }
        return typeof enCurrent === "string" ? enCurrent : fallback || keyPath;
      }
    }

    return typeof current === "string" ? current : fallback || keyPath;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);

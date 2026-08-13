"use client";

import { Flame, Star, Heart, Gem } from "lucide-react";
import styles from "./TopBar.module.css";

interface TopBarProps {
  courseName: string;
  targetLanguage?: string;
  streak: number;
  xp: number;
  hearts: number;
  gems?: number;
}

export default function TopBar({
  courseName,
  targetLanguage = "Spanish",
  streak,
  xp,
  hearts,
  gems = 500,
}: TopBarProps) {
  // Get appropriate flag emoji based on target language
  const getFlag = (lang: string) => {
    switch (lang.toLowerCase()) {
      case "spanish":
        return "🇪🇸";
      case "french":
        return "🇫🇷";
      case "german":
        return "🇩🇪";
      case "japanese":
        return "🇯🇵";
      default:
        return "🌐";
    }
  };

  return (
    <div className={styles.topBar}>
      <div className={styles.leftSection}>
        <div className={styles.courseBadge}>
          <span className={styles.flagIcon}>{getFlag(targetLanguage)}</span>
          <span>{courseName || "Course"}</span>
        </div>
      </div>

      <div className={styles.rightSection}>
        {/* Streak */}
        <div className={`${styles.statItem} ${styles.streak}`} title="Streak">
          <Flame className={styles.icon} fill="currentColor" />
          <span className={styles.statLabel}>{streak}</span>
        </div>

        {/* XP */}
        <div className={`${styles.statItem} ${styles.xp}`} title="Total XP">
          <Star className={styles.icon} fill="currentColor" />
          <span className={styles.statLabel}>{xp}</span>
        </div>

        {/* Hearts */}
        <div className={`${styles.statItem} ${styles.hearts}`} title="Hearts">
          <Heart className={styles.icon} fill="currentColor" />
          <span className={styles.statLabel}>{hearts}</span>
        </div>

        {/* Gems (Static display for premium polish) */}
        <div className={`${styles.statItem} ${styles.gems}`} title="Gems">
          <Gem className={styles.icon} fill="currentColor" />
          <span className={styles.statLabel}>{gems}</span>
        </div>
      </div>
    </div>
  );
}

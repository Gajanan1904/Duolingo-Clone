"use client";

import { Bell, Volume2, Palette, User, ChevronRight } from "lucide-react";
import styles from "./Settings.module.css";

interface SettingsSectionItem {
  label: string;
  value?: string;
  comingSoon?: boolean;
}

interface SettingsSection {
  title: string;
  icon: React.ReactNode;
  iconColor: string;
  items: SettingsSectionItem[];
}

const sections: SettingsSection[] = [
  {
    title: "Sound",
    icon: <Volume2 size={20} />,
    iconColor: "var(--color-blue)",
    items: [
      { label: "Sound Effects", comingSoon: true },
      { label: "Background Music", comingSoon: true },
      { label: "Speaking Exercises", comingSoon: true },
    ],
  },
  {
    title: "Notifications",
    icon: <Bell size={20} />,
    iconColor: "#FF9600",
    items: [
      { label: "Daily Reminder", comingSoon: true },
      { label: "Streak Reminders", comingSoon: true },
      { label: "Friend Activity", comingSoon: true },
    ],
  },
  {
    title: "Appearance",
    icon: <Palette size={20} />,
    iconColor: "var(--color-purple-dark)",
    items: [
      { label: "Dark Mode", comingSoon: true },
      { label: "Font Size", comingSoon: true },
    ],
  },
  {
    title: "Account",
    icon: <User size={20} />,
    iconColor: "var(--color-green)",
    items: [
      { label: "Username", value: "demo_user" },
      { label: "Learning Language", value: "Spanish" },
      { label: "Daily Goal", value: "20 XP / day" },
      { label: "Privacy Settings", comingSoon: true },
      { label: "Sign Out", comingSoon: true },
    ],
  },
];

export default function SettingsPage() {
  return (
    <div className={styles.container}>
      <h1 className={styles.pageTitle}>Settings</h1>

      {sections.map((section) => (
        <div key={section.title} className={styles.section}>
          <div className={styles.sectionHeader}>
            <div
              className={styles.sectionIcon}
              style={{ color: section.iconColor, backgroundColor: `${section.iconColor}18` }}
            >
              {section.icon}
            </div>
            <span className={styles.sectionTitle}>{section.title}</span>
          </div>

          <div className={styles.sectionItems}>
            {section.items.map((item) => (
              <div key={item.label} className={styles.settingRow}>
                <span className={styles.settingLabel}>{item.label}</span>
                {item.comingSoon ? (
                  <span className={styles.comingSoonBadge}>Coming Soon</span>
                ) : (
                  <div className={styles.settingRight}>
                    {item.value && (
                      <span className={styles.settingValue}>{item.value}</span>
                    )}
                    <ChevronRight size={16} className={styles.chevron} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      <div className={styles.appInfo}>
        <p>LinguaQuest v1.0</p>
        <p>"Learn a little. Grow every day."</p>
      </div>
    </div>
  );
}

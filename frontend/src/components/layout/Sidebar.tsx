"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, Trophy, User, Settings, Sparkles } from "lucide-react";
import styles from "./Sidebar.module.css";

export default function Sidebar() {
  const pathname = usePathname();

  // Hide sidebar/navigation when in a lesson
  if (pathname?.startsWith("/lesson/")) {
    return null;
  }

  const navItems = [
    { name: "Learn", href: "/", icon: Compass },
    { name: "Leaderboard", href: "/leaderboard", icon: Trophy },
    { name: "Profile", href: "/profile", icon: User },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className={styles.desktopSidebar}>
        <div className={styles.logoContainer}>
          <Sparkles className={styles.logoIcon} />
          <span className={styles.logoText}>LinguaQuest</span>
        </div>
        <nav className={styles.navMenu}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`${styles.navItem} ${isActive ? styles.navItemActive : ""}`}
              >
                <Icon className={styles.navIcon} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Mobile Bottom Navigation */}
      <nav className={styles.mobileBottomNav}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`${styles.mobileNavItem} ${isActive ? styles.mobileNavItemActive : ""}`}
            >
              <Icon className={styles.mobileNavIcon} />
              <span className={styles.mobileNavLabel}>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </>
  );
}

"use client";

import Link from "next/link";
import {
  MessageSquare,
  User,
  Utensils,
  Coffee,
  Users,
  Calendar,
  BookOpen,
  Lock,
  Crown,
  Check,
  Play,
} from "lucide-react";
import { Skill } from "../../types/api";
import styles from "./LearningPath.module.css";

interface SkillNodeProps {
  skill: Skill;
  index: number;
  activePopover: number | null;
  setActivePopover: (id: number | null) => void;
}

export default function SkillNode({
  skill,
  index,
  activePopover,
  setActivePopover,
}: SkillNodeProps) {
  // Stagger positions: Left, Center, Right, Center (loops every 4)
  const staggerPositions = [
    styles.staggerCenter,
    styles.staggerLeft,
    styles.staggerCenter,
    styles.staggerRight,
  ];
  const staggerClass = staggerPositions[index % 4];

  // Dynamic icon mapping based on title
  const getIcon = (title: string) => {
    const t = title.toLowerCase();
    if (t.includes("greeting")) return MessageSquare;
    if (t.includes("intro")) return User;
    if (t.includes("food") || t.includes("eat")) return Utensils;
    if (t.includes("drink") || t.includes("beverage")) return Coffee;
    if (t.includes("family") || t.includes("people")) return Users;
    if (t.includes("activit") || t.includes("life") || t.includes("day")) return Calendar;
    return BookOpen;
  };

  const Icon = getIcon(skill.title);
  const isLocked = skill.status === "locked";
  const isCompleted = skill.status === "completed";
  const isInProgress = skill.status === "in_progress";
  const isAvailable = skill.status === "available";

  const togglePopover = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isLocked) return;
    if (activePopover === skill.id) {
      setActivePopover(null);
    } else {
      setActivePopover(skill.id);
    }
  };

  // Progress ring math
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (skill.progress / 100) * circumference;

  return (
    <div className={`${styles.nodeContainer} ${staggerClass}`}>
      {/* Skill Node Circle */}
      <button
        onClick={togglePopover}
        className={`${styles.nodeCircle} ${
          isCompleted
            ? styles.completedNode
            : isInProgress
            ? styles.inProgressNode
            : isAvailable
            ? styles.availableNode
            : styles.lockedNode
        }`}
        disabled={isLocked}
        title={skill.title}
      >
        {/* Radial Progress Ring for In-Progress/Active nodes */}
        {(isInProgress || isAvailable) && (
          <svg className={styles.progressRingSvg}>
            <circle
              className={styles.progressRingBg}
              cx="56"
              cy="56"
              r={radius}
            />
            <circle
              className={styles.progressRingValue}
              cx="56"
              cy="56"
              r={radius}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
            />
          </svg>
        )}

        {/* Node Icons / Locks */}
        {isLocked ? (
          <Lock className={styles.nodeIcon} />
        ) : (
          <Icon className={styles.nodeIcon} />
        )}

        {/* Crowns Badge */}
        {!isLocked && skill.crowns > 0 && (
          <div className={styles.crownBadge}>
            <Crown className={styles.crownBadgeIcon} fill="currentColor" />
            <span style={{ marginLeft: "2px" }}>{skill.crowns}</span>
          </div>
        )}

        {/* Checkmark Badge for Completed */}
        {isCompleted && (
          <div className={styles.checkmarkBadge}>
            <Check className={styles.crownBadgeIcon} strokeWidth={3} />
          </div>
        )}
      </button>

      {/* Popover Details Card */}
      {activePopover === skill.id && (
        <div
          className={styles.popoverCard}
          onClick={(e) => e.stopPropagation()}
        >
          <div className={styles.popoverTitle}>{skill.title}</div>
          <div className={styles.popoverDesc}>{skill.description}</div>
          <div className={styles.popoverLessons}>
            Lesson {skill.completed_lessons} / {skill.total_lessons}
          </div>
          
          <Link
            href={`/lesson/${skill.lesson_ids?.[0] || skill.id}`}
            className="btn-tactile btn-green"
            style={{ width: "100%", gap: "8px", textDecoration: "none" }}
          >
            <Play size={16} fill="currentColor" />
            Start +10 XP
          </Link>
        </div>
      )}
    </div>
  );
}

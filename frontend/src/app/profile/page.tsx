"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { ProfileResponse } from "@/types/api";
import {
  Flame,
  Star,
  Heart,
  Trophy,
  BookOpen,
  Target,
  Zap,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import styles from "./Profile.module.css";

export default function ProfilePage() {
  const { loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refilling, setRefilling] = useState(false);
  const [refillMsg, setRefillMsg] = useState<string | null>(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getProfile();
      setProfile(data);
    } catch (err: any) {
      setError(err.message || "Failed to load profile.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading) {
      fetchProfile();
    }
  }, [authLoading]);

  const handleRefillHearts = async () => {
    setRefilling(true);
    setRefillMsg(null);
    try {
      const res = await api.refillHearts();
      if (res.success) {
        setRefillMsg(`Hearts refilled to ${res.hearts.current}/${res.hearts.max}!`);
        fetchProfile();
      }
    } catch (err: any) {
      setRefillMsg(err.message || "Could not refill hearts.");
    } finally {
      setRefilling(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.skeletonAvatar} />
        <div className={styles.skeletonText} />
        <div className={styles.skeletonGrid} />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState}>
        <AlertCircle size={56} color="var(--color-red)" />
        <p>{error}</p>
        <button onClick={fetchProfile} className="btn-tactile btn-blue" style={{ gap: "8px", display: "flex", alignItems: "center" }}>
          <RefreshCw size={16} />
          Retry
        </button>
      </div>
    );
  }

  if (!profile) return null;

  const { user, stats, progress } = profile;
  const dailyGoalPercent = Math.min(100, (stats.daily_xp / stats.daily_xp_goal) * 100);

  return (
    <div className={styles.container}>
      {/* Avatar + Name Section */}
      <div className={styles.profileHeader}>
        <div className={styles.avatarCircle}>
          {user.username.charAt(0).toUpperCase()}
        </div>
        <h1 className={styles.username}>{user.username}</h1>
        {user.first_name && (
          <p className={styles.fullName}>
            {user.first_name} {user.last_name}
          </p>
        )}
      </div>

      {/* Stat cards grid */}
      <div className={styles.statsGrid}>
        <StatCard
          icon={<Star fill="currentColor" size={28} />}
          color="var(--color-yellow)"
          label="Total XP"
          value={stats.total_xp.toLocaleString()}
        />
        <StatCard
          icon={<Flame fill="currentColor" size={28} />}
          color="#FF9600"
          label="Streak"
          value={`${stats.current_streak} day${stats.current_streak !== 1 ? "s" : ""}`}
        />
        <StatCard
          icon={<Zap fill="currentColor" size={28} />}
          color="var(--color-purple-dark)"
          label="Longest Streak"
          value={`${stats.longest_streak} days`}
        />
        <StatCard
          icon={<Heart fill="currentColor" size={28} />}
          color="var(--color-red)"
          label="Hearts"
          value={`${stats.hearts} / ${stats.max_hearts}`}
        />
        <StatCard
          icon={<Trophy fill="currentColor" size={28} />}
          color="var(--color-green)"
          label="Skills Done"
          value={progress.skills_completed.toString()}
        />
        <StatCard
          icon={<BookOpen size={28} />}
          color="var(--color-blue)"
          label="Lessons Done"
          value={progress.lessons_completed.toString()}
        />
      </div>

      {/* Daily Goal Progress */}
      <div className={styles.goalCard}>
        <div className={styles.goalHeader}>
          <Target size={20} color="var(--color-green)" />
          <span className={styles.goalTitle}>Daily Goal</span>
          <span className={styles.goalNumbers}>
            {stats.daily_xp} / {stats.daily_xp_goal} XP
          </span>
        </div>
        <div className={styles.goalTrack}>
          <div
            className={styles.goalProgress}
            style={{ width: `${dailyGoalPercent}%` }}
          />
        </div>
        <p className={styles.goalCaption}>
          {dailyGoalPercent >= 100
            ? "🎉 Daily goal reached! Great work!"
            : `${stats.daily_xp_goal - stats.daily_xp} XP left to reach your daily goal`}
        </p>
      </div>

      {/* Heart refill action */}
      {stats.hearts < stats.max_hearts && (
        <div className={styles.refillSection}>
          <p className={styles.refillLabel}>Your hearts are not full</p>
          {refillMsg && (
            <p className={styles.refillMsg}>{refillMsg}</p>
          )}
          <button
            onClick={handleRefillHearts}
            className="btn-tactile btn-red"
            disabled={refilling}
            style={{ width: "100%", gap: "8px", display: "flex", alignItems: "center", justifyContent: "center" }}
          >
            <Heart fill="currentColor" size={18} />
            {refilling ? "Refilling..." : "Refill Hearts"}
          </button>
        </div>
      )}
    </div>
  );
}

function StatCard({
  icon,
  color,
  label,
  value,
}: {
  icon: React.ReactNode;
  color: string;
  label: string;
  value: string;
}) {
  return (
    <div className={styles.statCard}>
      <div className={styles.statIcon} style={{ color }}>
        {icon}
      </div>
      <div className={styles.statLabel}>{label}</div>
      <div className={styles.statValue}>{value}</div>
    </div>
  );
}

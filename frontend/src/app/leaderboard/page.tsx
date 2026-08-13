"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { LeaderboardEntry, LeaderboardResponse } from "@/types/api";
import { Medal, AlertCircle, RefreshCw, Trophy } from "lucide-react";
import styles from "./Leaderboard.module.css";

export default function LeaderboardPage() {
  const { loading: authLoading } = useAuth();
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLeaderboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getLeaderboard();
      setData(res);
    } catch (err: any) {
      setError(err.message || "Failed to load leaderboard.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading) {
      fetchLeaderboard();
    }
  }, [authLoading]);

  if (loading) {
    return (
      <div className={styles.container}>
        <h1 className={styles.pageTitle}>Leaderboard</h1>
        {[...Array(5)].map((_, i) => (
          <div key={i} className={styles.skeletonRow} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState}>
        <AlertCircle size={56} color="var(--color-red)" />
        <p>{error}</p>
        <button
          onClick={fetchLeaderboard}
          className="btn-tactile btn-blue"
          style={{ gap: "8px", display: "flex", alignItems: "center" }}
        >
          <RefreshCw size={16} />
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  const { leaderboard, current_user_rank } = data;
  const top3 = leaderboard.slice(0, 3);
  const rest = leaderboard.slice(3);

  return (
    <div className={styles.container}>
      <h1 className={styles.pageTitle}>Leaderboard</h1>
      <p className={styles.pageSubtitle}>Your rank: #{current_user_rank}</p>

      {/* Podium Section for Top 3 */}
      {top3.length > 0 && (
        <div className={styles.podium}>
          {/* 2nd place */}
          {top3[1] && (
            <PodiumItem
              entry={top3[1]}
              place={2}
              isCurrentUser={top3[1].rank === current_user_rank}
            />
          )}
          {/* 1st place (center, tallest) */}
          {top3[0] && (
            <PodiumItem
              entry={top3[0]}
              place={1}
              isCurrentUser={top3[0].rank === current_user_rank}
            />
          )}
          {/* 3rd place */}
          {top3[2] && (
            <PodiumItem
              entry={top3[2]}
              place={3}
              isCurrentUser={top3[2].rank === current_user_rank}
            />
          )}
        </div>
      )}

      {/* Rest of Leaderboard */}
      <div className={styles.list}>
        {rest.map((entry) => (
          <LeaderboardRow
            key={entry.rank}
            entry={entry}
            isCurrentUser={entry.rank === current_user_rank}
          />
        ))}
        {rest.length === 0 && leaderboard.length > 0 && (
          <p style={{ textAlign: "center", color: "var(--color-muted)", fontWeight: "600" }}>
            Only top {top3.length} shown in the podium above.
          </p>
        )}
      </div>
    </div>
  );
}

function PodiumItem({
  entry,
  place,
  isCurrentUser,
}: {
  entry: LeaderboardEntry;
  place: 1 | 2 | 3;
  isCurrentUser: boolean;
}) {
  const heightMap = { 1: "160px", 2: "120px", 3: "100px" };
  const colorMap = {
    1: "var(--color-yellow)",
    2: "#CDCDCD",
    3: "#CD7F32",
  };
  const glowMap = {
    1: "0 0 20px rgba(255, 200, 0, 0.3)",
    2: "none",
    3: "none",
  };
  const medalIcons = {
    1: "🥇",
    2: "🥈",
    3: "🥉",
  };

  return (
    <div
      className={`${styles.podiumItem} ${isCurrentUser ? styles.podiumCurrentUser : ""}`}
      style={{ alignSelf: "flex-end", order: place === 1 ? 0 : place }}
    >
      <div className={styles.podiumLabel}>{entry.user.username}</div>
      <div className={styles.podiumXP}>{entry.xp.toLocaleString()} XP</div>
      <div
        className={styles.podiumBlock}
        style={{
          height: heightMap[place],
          backgroundColor: colorMap[place],
          boxShadow: glowMap[place],
        }}
      >
        <div className={styles.podiumMedal}>{medalIcons[place]}</div>
      </div>
    </div>
  );
}

function LeaderboardRow({
  entry,
  isCurrentUser,
}: {
  entry: LeaderboardEntry;
  isCurrentUser: boolean;
}) {
  return (
    <div className={`${styles.row} ${isCurrentUser ? styles.rowCurrentUser : ""}`}>
      <span className={styles.rank}>#{entry.rank}</span>
      <div className={styles.rowAvatar}>
        {entry.user.username.charAt(0).toUpperCase()}
      </div>
      <span className={styles.rowUsername}>{entry.user.username}</span>
      <span className={styles.rowXP}>{entry.xp.toLocaleString()} XP</span>
    </div>
  );
}

"use client";

import { useEffect, useState, useRef } from "react";
import TopBar from "@/components/gamification/TopBar";
import SkillNode from "@/components/learning-path/SkillNode";
import { api } from "@/services/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { LearningPathResponse, Stats } from "@/types/api";
import styles from "@/components/learning-path/LearningPath.module.css";
import { AlertCircle, RefreshCw } from "lucide-react";

export default function Home() {
  const { loading: authLoading } = useAuth();
  const [pathData, setPathData] = useState<LearningPathResponse | null>(null);
  const [statsData, setStatsData] = useState<Stats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activePopover, setActivePopover] = useState<number | null>(null);
  const isFetching = useRef(false);

  const fetchData = async () => {
    if (isFetching.current) return;
    isFetching.current = true;
    setLoading(true);
    setError(null);
    try {
      const path = await api.getPath();
      setPathData(path);
      try {
        const stats = await api.getStats();
        setStatsData(stats);
      } catch (statsErr) {
        console.warn("Could not fetch stats:", statsErr);
      }
    } catch (err: any) {
      console.error("Error fetching path data:", err);
      if (err.code === "UNAUTHORIZED") {
        setError("You are not authenticated. Please refresh or check session cookies.");
      } else {
        setError(err.message || "Failed to load learning path. Please try again.");
      }
    } finally {
      setLoading(false);
      isFetching.current = false;
    }
  };

  useEffect(() => {
    if (!authLoading) {
      fetchData();
    }
  }, [authLoading]);

  useEffect(() => {
    // Close popover when clicking anywhere else
    const handleGlobalClick = () => {
      setActivePopover(null);
    };

    window.addEventListener("click", handleGlobalClick);
    return () => {
      window.removeEventListener("click", handleGlobalClick);
    };
  }, []);

  if (loading || authLoading) {
    return (
      <div style={{ width: "100%", maxWidth: "600px", margin: "0 auto", padding: "20px" }}>
        <div className={styles.skeletonBanner} />
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "30px" }}>
          <div className={styles.skeletonCircle} style={{ transform: "translateX(0px)" }} />
          <div className={styles.skeletonCircle} style={{ transform: "translateX(-50px)" }} />
          <div className={styles.skeletonCircle} style={{ transform: "translateX(0px)" }} />
          <div className={styles.skeletonCircle} style={{ transform: "translateX(50px)" }} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "80vh", padding: "24px", textAlign: "center", maxWidth: "450px", margin: "0 auto" }}>
        <AlertCircle size={64} color="var(--color-red)" style={{ marginBottom: "16px", filter: "drop-shadow(0 2px 0 var(--color-red-border))" }} />
        <h2 style={{ fontSize: "24px", fontWeight: "800", marginBottom: "12px" }}>Something went wrong</h2>
        <p style={{ color: "var(--color-muted)", fontSize: "16px", marginBottom: "24px", lineHeight: "1.5" }}>
          {error}
        </p>
        <button onClick={fetchData} className="btn-tactile btn-blue" style={{ gap: "8px" }}>
          <RefreshCw size={18} />
          Retry Connection
        </button>
      </div>
    );
  }

  // Get banner color based on unit order/id
  const getBannerColor = (order: number) => {
    const banners = [styles.unitBanner, styles.unitBannerBlue, styles.unitBannerPurple];
    return banners[(order - 1) % banners.length];
  };

  return (
    <div style={{ width: "100%", display: "flex", flexDirection: "column" }}>
      {/* Top statistics panel */}
      {statsData && pathData && (
        <TopBar
          courseName={pathData.course.name}
          targetLanguage={pathData.course.target_language}
          streak={statsData.current_streak}
          xp={statsData.total_xp}
          hearts={statsData.hearts}
        />
      )}

      {/* Learning Path Container */}
      <div className={styles.container}>
        {pathData?.units.map((unit) => (
          <div key={unit.id} style={{ width: "100%", marginBottom: "48px" }}>
            {/* Unit Header Card */}
            <div className={getBannerColor(unit.order)}>
              <div className={styles.unitNumber}>Unit {unit.order}</div>
              <h2 className={styles.unitTitle}>{unit.title}</h2>
              <div className={styles.unitDesc}>{unit.description}</div>
            </div>

            {/* Vertical snake path */}
            <div className={styles.nodesWrapper}>
              <div className={styles.pathLine} />
              {unit.skills.map((skill, index) => (
                <SkillNode
                  key={skill.id}
                  skill={skill}
                  index={index}
                  activePopover={activePopover}
                  setActivePopover={setActivePopover}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

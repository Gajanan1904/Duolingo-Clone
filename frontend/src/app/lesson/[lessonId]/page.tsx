"use client";

import { useEffect, useState, useRef, use } from "react";
import { useRouter } from "next/navigation";
import { X, Heart, Sparkles, CheckCircle2, XCircle, ChevronRight, AlertCircle, RefreshCw } from "lucide-react";
import { api } from "@/services/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { Exercise, HeartsInfo, CompleteLessonResponse } from "@/types/api";
import ExerciseRenderer from "@/components/lesson/ExerciseRenderer";
import styles from "@/components/lesson/LessonPlayer.module.css";

interface LessonPageProps {
  params: Promise<{ lessonId: string }>;
}

export default function LessonPage({ params }: LessonPageProps) {
  const router = useRouter();
  const { loading: authLoading } = useAuth();
  
  // Resolve params using React.use()
  const resolvedParams = use(params);
  const lessonId = parseInt(resolvedParams.lessonId, 10);

  // Lesson state
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [exerciseQueue, setExerciseQueue] = useState<Exercise[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [lessonTitle, setLessonTitle] = useState<string>("Lesson");
  
  // Active question state
  const [selectedAnswer, setSelectedAnswer] = useState<any>(null);
  const [isAnswerChecked, setIsAnswerChecked] = useState<boolean>(false);
  const [isCorrect, setIsCorrect] = useState<boolean>(false);
  const [feedbackMsg, setFeedbackMsg] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);
  
  // Attempt / Gamification state
  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [hearts, setHearts] = useState<HeartsInfo>({ current: 5, max: 5 });
  const [deductHeartAnim, setDeductHeartAnim] = useState<boolean>(false);
  const [isOutOfHearts, setIsOutOfHearts] = useState<boolean>(false);
  const [refilling, setRefilling] = useState<boolean>(false);

  // Loading & general errors
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Celebration state
  const [showCelebration, setShowCelebration] = useState<boolean>(false);
  const [completionData, setCompletionData] = useState<CompleteLessonResponse | null>(null);

  const fetchLessonData = async () => {
    setLoading(true);
    setError(null);
    try {
      // First fetch the user stats to get current hearts count
      const stats = await api.getStats();
      setHearts({ current: stats.hearts, max: stats.max_hearts });
      if (stats.hearts <= 0) {
        setIsOutOfHearts(true);
      }

      // Fetch the lesson
      const lesson = await api.getLesson(lessonId);
      setLessonTitle(lesson.title);
      setExercises(lesson.exercises);
      setExerciseQueue([...lesson.exercises]);
      setCurrentIndex(0);
    } catch (err: any) {
      console.error("Error loading lesson:", err);
      if (err.code === "UNAUTHORIZED") {
        setError("Please login or ensure session cookies are enabled.");
      } else {
        setError(err.message || "Failed to load lesson. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && lessonId) {
      fetchLessonData();
    }
  }, [authLoading, lessonId]);

  const currentExercise = exerciseQueue[currentIndex];
  const progressPercent =
    exerciseQueue.length > 0
      ? (currentIndex / exerciseQueue.length) * 100
      : 0;

  // Handle checking answers
  const handleCheck = async () => {
    if (submitting || !selectedAnswer || isAnswerChecked) return;
    setSubmitting(true);
    setError(null);

    try {
      // Pass the answer object directly — api.ts forwards it as-is
      // Shapes: { value: string } | { words: string[] } | { pairs: {...} }
      const res = await api.submitAnswer(lessonId, currentExercise.id, selectedAnswer);
      handleAnswerResponse(res);
    } catch (err: any) {
      console.error("Error submitting answer:", err);
      // If error is out of hearts
      if (err.code === "INVALID_ATTEMPT" && err.message.toLowerCase().includes("heart")) {
        setHearts((prev) => ({ ...prev, current: 0 }));
        setIsOutOfHearts(true);
      } else {
        setError(err.message || "Something went wrong while checking your answer.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleAnswerResponse = (res: any) => {
    // Record attempt ID from first submission
    if (res.attempt_id) {
      setAttemptId(res.attempt_id);
    }

    setIsCorrect(res.correct);
    setFeedbackMsg(res.feedback?.message || (res.correct ? "Correct!" : "Not quite."));
    setIsAnswerChecked(true);

    // Heart deduction animation if incorrect
    if (!res.correct) {
      if (res.hearts.current < hearts.current) {
        setDeductHeartAnim(true);
        setTimeout(() => setDeductHeartAnim(false), 800);
      }
      setHearts({ current: res.hearts.current, max: res.hearts.max });

      // Put incorrect exercise back to the end of the queue
      setExerciseQueue((prev) => [...prev, currentExercise]);

      // Check if failed out of hearts
      if (res.hearts.current <= 0 || res.lesson.status === "failed") {
        setIsOutOfHearts(true);
      }
    }
  };

  // Continue to next question or complete lesson
  const handleContinue = async () => {
    setError(null);
    
    // Reset active question state
    setSelectedAnswer(null);
    setIsAnswerChecked(false);
    setFeedbackMsg("");

    const nextIndex = currentIndex + 1;
    if (nextIndex < exerciseQueue.length) {
      setCurrentIndex(nextIndex);
    } else {
      // Completed all exercises in queue! Call complete lesson API
      setSubmitting(true);
      try {
        if (!attemptId) {
          throw new Error("No active attempt found for this lesson.");
        }
        const completeRes = await api.completeLesson(lessonId, attemptId);
        setCompletionData(completeRes);
        setShowCelebration(true);
      } catch (err: any) {
        console.error("Error completing lesson:", err);
        setError(err.message || "Failed to complete lesson. Please try again.");
      } finally {
        setSubmitting(false);
      }
    }
  };

  // Refill hearts handler
  const handleRefillHearts = async () => {
    setRefilling(true);
    setError(null);
    try {
      const res = await api.refillHearts();
      if (res.success) {
        setHearts({ current: res.hearts.current, max: res.hearts.max });
        setIsOutOfHearts(false);
      }
    } catch (err: any) {
      console.error("Error refilling hearts:", err);
      setError(err.message || "Failed to refill hearts. Please try again.");
    } finally {
      setRefilling(false);
    }
  };

  const handleQuit = () => {
    router.push("/");
  };

  if (loading) {
    return (
      <div className={styles.wrapper} style={{ justifyContent: "center", alignItems: "center" }}>
        <div className={styles.skeletonBanner} style={{ maxWidth: "500px" }} />
        <div style={{ fontSize: "16px", fontWeight: "700", color: "var(--color-muted)" }}>
          Loading lesson elements...
        </div>
      </div>
    );
  }

  if (error && !isAnswerChecked && !showCelebration) {
    return (
      <div className={styles.wrapper} style={{ justifyContent: "center", alignItems: "center", padding: "20px", textAlign: "center" }}>
        <AlertCircle size={64} color="var(--color-red)" style={{ marginBottom: "16px" }} />
        <h2 style={{ fontSize: "24px", fontWeight: "800", marginBottom: "12px" }}>Connection Error</h2>
        <p style={{ color: "var(--color-muted)", fontSize: "16px", marginBottom: "24px", maxWidth: "400px" }}>
          {error}
        </p>
        <div style={{ display: "flex", gap: "12px" }}>
          <button onClick={fetchLessonData} className="btn-tactile btn-blue" style={{ gap: "8px" }}>
            <RefreshCw size={18} />
            Retry
          </button>
          <button onClick={handleQuit} className="btn-tactile btn-red">
            Quit
          </button>
        </div>
      </div>
    );
  }

  // Render Celebration / Completion Modal Screen
  if (showCelebration && completionData) {
    const dailyGoalProgress = Math.min(
      100,
      (completionData.stats.daily_xp / completionData.stats.daily_xp_goal) * 100
    );

    return (
      <div className={styles.wrapper} style={{ overflowY: "auto", padding: "40px 20px" }}>
        <div style={{ maxWidth: "480px", width: "100%", margin: "auto", textAlign: "center" }} className="animate-fade-in">
          <div style={{ fontSize: "80px", marginBottom: "16px" }}>🎉</div>
          
          <h1 style={{ fontSize: "32px", fontWeight: "800", color: "var(--color-blue)", marginBottom: "8px" }}>
            LESSON COMPLETE!
          </h1>
          <p style={{ fontSize: "16px", color: "var(--color-muted)", fontWeight: "600", marginBottom: "32px" }}>
            Great job! You finished all exercises.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "20px", marginBottom: "40px" }}>
            {/* XP Earned Card */}
            <div className="card-tactile" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontWeight: "800", color: "var(--color-yellow-border)" }}>XP Earned</span>
              <span style={{ fontSize: "20px", fontWeight: "800", color: "var(--color-yellow)" }}>
                +{completionData.rewards.xp_earned} XP
              </span>
            </div>

            {/* Skill Progress Card */}
            <div className="card-tactile" style={{ display: "flex", flexDirection: "column", gap: "10px", textAlign: "left" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontWeight: "800" }}>
                <span>Skill Progress</span>
                <span style={{ color: "var(--color-green)" }}>{completionData.skill.progress}%</span>
              </div>
              <div style={{ height: "12px", backgroundColor: "var(--color-border)", borderRadius: "6px", overflow: "hidden" }}>
                <div
                  style={{
                    height: "100%",
                    backgroundColor: "var(--color-green)",
                    width: `${completionData.skill.progress}%`,
                    borderRadius: "6px",
                  }}
                />
              </div>
              <div style={{ fontSize: "13px", color: "var(--color-muted)", fontWeight: "700" }}>
                Crowns: {completionData.skill.crowns}
              </div>
            </div>

            {/* Streak & Daily XP Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div className="card-tactile">
                <div style={{ fontSize: "24px", marginBottom: "4px" }}>🔥</div>
                <div style={{ fontSize: "12px", color: "var(--color-muted)", fontWeight: "800" }}>STREAK</div>
                <div style={{ fontSize: "18px", fontWeight: "800" }}>
                  {completionData.stats.current_streak} Day{completionData.stats.current_streak > 1 ? "s" : ""}
                </div>
              </div>
              <div className="card-tactile">
                <div style={{ fontSize: "24px", marginBottom: "4px" }}>🎯</div>
                <div style={{ fontSize: "12px", color: "var(--color-muted)", fontWeight: "800" }}>DAILY GOAL</div>
                <div style={{ fontSize: "18px", fontWeight: "800" }}>
                  {completionData.stats.daily_xp} / {completionData.stats.daily_xp_goal} XP
                </div>
              </div>
            </div>
          </div>

          <button onClick={handleQuit} className="btn-tactile btn-green" style={{ width: "100%" }}>
            Continue to home
          </button>
        </div>
      </div>
    );
  }

  // Render main player interface
  return (
    <div className={styles.wrapper}>
      {/* Header bar */}
      <header className={styles.header}>
        <button className={styles.closeButton} onClick={handleQuit} title="Quit Lesson">
          <X size={28} />
        </button>

        {/* Lesson Progress Bar */}
        <div className={styles.progressContainer}>
          <div className={styles.progressBar} style={{ width: `${progressPercent}%` }} />
        </div>

        {/* Hearts indicator */}
        <div className={styles.heartsContainer}>
          <Heart
            className={`${styles.heartIcon} ${deductHeartAnim ? styles.heartDeduct : ""}`}
            fill="currentColor"
          />
          <span>{hearts.current}</span>
        </div>
      </header>

      {/* Central content container */}
      {currentExercise && (
        <main className={styles.workspace}>
          <h2 className={styles.exerciseTitle}>{currentExercise.question}</h2>

          <div style={{ margin: "24px 0", flex: 1, display: "flex", alignItems: "center" }}>
            <ExerciseRenderer
              exercise={currentExercise}
              selectedAnswer={selectedAnswer}
              onAnswerChange={(val) => {
                if (!isAnswerChecked) setSelectedAnswer(val);
              }}
              disabled={isAnswerChecked}
            />
          </div>
        </main>
      )}

      {/* Bottom check actions panel */}
      <div
        className={`${styles.bottomBar} ${
          isAnswerChecked
            ? isCorrect
              ? styles.bottomBarCorrect
              : styles.bottomBarIncorrect
            : ""
        }`}
      >
        <div className={styles.bottomBarContent}>
          {/* Answer State message feedback */}
          {isAnswerChecked ? (
            <div className={styles.feedbackMessage}>
              <div className={styles.feedbackIcon}>
                {isCorrect ? (
                  <CheckCircle2 className={styles.iconCorrect} size={28} fill="currentColor" />
                ) : (
                  <XCircle className={styles.iconIncorrect} size={28} fill="currentColor" />
                )}
              </div>
              <div className={styles.feedbackText}>
                <span className={styles.feedbackHeader}>
                  {isCorrect ? "Awesome! You got it." : "Not quite right."}
                </span>
                <span className={styles.feedbackSub}>{feedbackMsg}</span>
              </div>
            </div>
          ) : (
            // Placeholder text or error
            <div style={{ color: "var(--color-red)", fontWeight: "600" }}>
              {error && <span>{error}</span>}
            </div>
          )}

          {/* Action buttons */}
          {isAnswerChecked ? (
            <button
              onClick={handleContinue}
              className={`${styles.bottomButton} btn-tactile ${isCorrect ? "btn-green" : "btn-red"}`}
            >
              Continue
            </button>
          ) : (
            <button
              onClick={handleCheck}
              disabled={!selectedAnswer || submitting}
              className={`${styles.bottomButton} btn-tactile btn-green`}
            >
              {submitting ? "Checking..." : "Check"}
            </button>
          )}
        </div>
      </div>

      {/* Failure out-of-hearts modal */}
      {isOutOfHearts && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <div className={styles.modalIcon} style={{ color: "var(--color-red)" }}>
              <Heart size={64} fill="currentColor" />
            </div>
            <h3 className={styles.modalTitle}>No Hearts Left!</h3>
            <p className={styles.modalDesc}>
              You made a few mistakes and ran out of hearts. You can practice to refill them and continue this lesson, or go back home.
            </p>
            <div className={styles.modalActions}>
              <button
                onClick={handleRefillHearts}
                className="btn-tactile btn-blue"
                disabled={refilling}
                style={{ width: "100%" }}
              >
                {refilling ? "Refilling..." : "Refill Hearts (+5)"}
              </button>
              <button
                onClick={handleQuit}
                className="btn-tactile btn-red"
                style={{ width: "100%" }}
              >
                Quit Lesson
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

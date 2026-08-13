import { apiClient } from "./apiClient";

import {
  LearningPathResponse,
  Lesson,
  SubmitAnswerResponse,
  CompleteLessonResponse,
  ProfileResponse,
  Stats,
  LeaderboardResponse,
  HeartRefillResponse,
} from "../types/api";

type SessionUser = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
};

type SessionResponse = {
  authenticated: boolean;
  user: SessionUser | null;
};

type ExerciseAnswer = {
  value?: string;
  words?: string[];
  pairs?: Record<string, string>;
};

export const api = {
  /**
   * GET /api/auth/session/
   *
   * Bootstraps the Django browser session.
   * The browser receives sessionid + csrftoken cookies.
   */
  ensureSession: () =>
    apiClient.get<SessionResponse>("/api/auth/session/"),

  /**
   * GET /api/path/
   *
   * Returns the complete learning path including:
   * course → units → skills → progress.
   */
  getPath: () =>
    apiClient.get<LearningPathResponse>("/api/path/"),

  /**
   * GET /api/lessons/{lesson_id}/
   *
   * Returns a playable lesson without exposing correct answers.
   */
  getLesson: (lessonId: number) =>
    apiClient.get<Lesson>(`/api/lessons/${lessonId}/`),

  /**
   * POST /api/lessons/{lesson_id}/answer/
   *
   * Submit one exercise answer.
   */
  submitAnswer: (
    lessonId: number,
    exerciseId: number,
    answer: ExerciseAnswer,
  ) =>
    apiClient.post<SubmitAnswerResponse>(
      `/api/lessons/${lessonId}/answer/`,
      {
        exercise_id: exerciseId,
        answer,
      },
    ),

  /**
   * POST /api/lessons/{lesson_id}/complete/
   *
   * Complete the active lesson attempt.
   */
  completeLesson: (
    lessonId: number,
    attemptId: number,
  ) =>
    apiClient.post<CompleteLessonResponse>(
      `/api/lessons/${lessonId}/complete/`,
      {
        attempt_id: attemptId,
      },
    ),

  /**
   * GET /api/profile/
   *
   * Returns the learner profile and progress statistics.
   */
  getProfile: () =>
    apiClient.get<ProfileResponse>("/api/profile/"),

  /**
   * GET /api/stats/
   *
   * Returns current XP, streak, hearts and related stats.
   */
  getStats: () =>
    apiClient.get<Stats>("/api/stats/"),

  /**
   * GET /api/leaderboard/
   *
   * Returns the learner leaderboard.
   */
  getLeaderboard: () =>
    apiClient.get<LeaderboardResponse>("/api/leaderboard/"),

  /**
   * POST /api/practice/hearts/
   *
   * Refill the learner's hearts.
   */
  refillHearts: () =>
    apiClient.post<HeartRefillResponse>(
      "/api/practice/hearts/",
      {},
    ),
};
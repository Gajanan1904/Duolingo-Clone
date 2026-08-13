export interface Course {
  id: number;
  name: string;
  source_language: string;
  target_language: string;
}

export type SkillStatus = "locked" | "available" | "in_progress" | "completed";

export interface Skill {
  id: number;
  title: string;
  description: string;
  order: number;
  status: SkillStatus;
  progress: number; // 0-100
  crowns: number; // 0 or greater
  total_lessons: number;
  completed_lessons: number;
  lesson_ids: number[]; // ordered list of lesson IDs for this skill
}

export interface Unit {
  id: number;
  title: string;
  description: string;
  order: number;
  skills: Skill[];
}

export interface LearningPathResponse {
  course: Course;
  units: Unit[];
}

export type ExerciseType =
  | "multiple_choice"
  | "translate"
  | "word_bank"
  | "match_pairs"
  | "fill_blank"
  | "type_answer";

export interface MultipleChoiceData {
  options: string[];
}

export interface TranslateData {
  source_text: string;
}

export interface WordBankData {
  words: string[];
}

export interface MatchPairsData {
  pairs: {
    id: string;
    left: string;
    right: string;
  }[];
}

export interface FillBlankData {
  // Can be empty object as per contract or contain options/sentence parts
  [key: string]: any;
}

export interface TypeAnswerData {
  source_text: string;
}

export type ExerciseData =
  | MultipleChoiceData
  | TranslateData
  | WordBankData
  | MatchPairsData
  | FillBlankData
  | TypeAnswerData;

export interface Exercise {
  id: number;
  type: ExerciseType;
  question: string;
  data: any; // Using exact shape per exercise type
  order: number;
}

export interface Lesson {
  id: number;
  title: string;
  skill_id: number;
  xp_reward: number;
  total_exercises: number;
  exercises: Exercise[];
}

export interface SubmitAnswerRequest {
  exercise_id: number;
  answer: {
    value: string;
  };
}

export interface HeartsInfo {
  current: number;
  max: number;
}

export interface SubmitAnswerResponse {
  correct: boolean;
  exercise_id: number;
  attempt_id: number; // Return attempt ID from backend
  feedback: {
    message: string;
  };
  hearts: HeartsInfo;
  lesson: {
    status: "in_progress" | "completed";
  };
}

export interface CompleteLessonRequest {
  attempt_id: number;
}

export interface CompleteLessonResponse {
  success: boolean;
  lesson: {
    id: number;
    status: "completed";
  };
  rewards: {
    xp_earned: number;
  };
  skill: {
    id: number;
    progress: number;
    crowns: number;
    status: SkillStatus;
  };
  stats: {
    total_xp: number;
    daily_xp: number;
    daily_xp_goal: number;
    current_streak: number;
    hearts: number;
  };
}

export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
}

export interface Stats {
  total_xp: number;
  current_streak: number;
  longest_streak: number;
  daily_xp: number;
  daily_xp_goal: number;
  hearts: number;
  max_hearts: number;
}

export interface ProfileProgress {
  skills_completed: number;
  lessons_completed: number;
}

export interface ProfileResponse {
  user: User;
  stats: Stats;
  progress: ProfileProgress;
}

export interface LeaderboardUser {
  id: number;
  username: string;
}

export interface LeaderboardEntry {
  rank: number;
  user: LeaderboardUser;
  xp: number;
}

export interface LeaderboardResponse {
  leaderboard: LeaderboardEntry[];
  current_user_rank: number;
}

export interface HeartRefillResponse {
  success: boolean;
  hearts: HeartsInfo;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

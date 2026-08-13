# LinguaQuest(Duolingo-Clone)

### A language-learning platform where the backend owns the truth.

> A full-stack, production-oriented language learning platform inspired by modern language-learning applications, built with Next.js, TypeScript, Django REST Framework, and SQLite.

**Live Demo:** https://duolingo-clone-eight-eta.vercel.app

**Backend API:** https://duolingo-clone-c6y6.onrender.com

**GitHub:** https://github.com/Gajanan1904/Duolingo-Clone

---

## 🚀 What is LinguaQuest?

LinguaQuest is a full-stack language-learning platform built around a simple engineering principle:

> **The frontend displays the game. The backend decides the game.**

Instead of treating the project as only a UI clone, the implementation focuses on building the systems underneath the learning experience:

- Learning paths
- Units and skills
- Interactive lessons
- Multiple exercise types
- Answer validation
- Lesson attempts
- XP rewards
- Hearts
- Daily goals
- Streaks
- Skill progression
- Crowns
- Leaderboards
- Learner profiles
- Session authentication
- CSRF protection
- Production deployment

The application is deployed with the frontend on **Vercel** and the Django backend on **Render**.

---

# 🎯 The Core Idea

A learning application has an important trust boundary.

The browser should **not** be trusted to decide:

- whether an answer is correct
- how much XP was earned
- whether a lesson was completed
- whether a skill was completed
- whether a streak should increase
- whether rewards should be granted
- whether a learner has enough hearts

Therefore, LinguaQuest follows a backend-authoritative model.

```text
                 ┌─────────────────────────┐
                 │        FRONTEND         │
                 │                         │
                 │  Displays the lesson    │
                 │  Collects user input    │
                 │  Displays feedback      │
                 └────────────┬────────────┘
                              │
                              │ API Request
                              ▼
                 ┌─────────────────────────┐
                 │        BACKEND          │
                 │                         │
                 │  Validates request      │
                 │  Evaluates answer       │
                 │  Updates attempt        │
                 │  Calculates rewards     │
                 │  Updates progress       │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │       DATABASE          │
                 │                         │
                 │  Users                  │
                 │  Courses                │
                 │  Lessons                │
                 │  Exercises              │
                 │  Progress               │
                 │  Gamification           │
                 └─────────────────────────┘
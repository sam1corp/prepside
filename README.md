# BUET AI Exam Engine — v12

This build extends the curated question bank with selected written Physics questions from the supplied 2026 Physics 1st and 2nd Paper concept books.

## Question-bank policy
- Written questions only; MCQs are excluded.
- Prefer hard / medium-hard questions that are multi-step and time-consuming for a written exam.
- Previous-year written questions are allowed.
- Questions remain in Bangla; mathematical/scientific notation is kept in standard LaTeX/Latin notation.
- Only essential diagrams/graphs are stored as question media. Full source pages are not shown to students.
- No generative AI is used for question-bank creation or exam generation.
- AI is reserved for the future grading stage.

## Current bank
- 168 curated questions total (including the new Chemistry and Physics Chapter 2 written-bank additions).
- 69 Physics questions total after the Vector Chapter 2 written-question import.
- Physics additions cover high-confidence candidates from multiple chapters; ambiguous scans were left out rather than guessed.

## Run
Backend:
`python -m uvicorn app.main:app --reload --port 8000`

Frontend:
`npm install`
`npm run dev`

## Subscription checkout URL
Set `VITE_SUBSCRIPTION_BUY_URL` in the frontend environment to the real subscription/payment checkout website. If it is left blank, the Home subscription CTA opens the in-app Subscription page and the plan buttons explain how to configure the checkout URL.

## Settings
The Settings page now includes Profile, Subscription, Security settings, Logout, and About us. Profile name updates are saved through `PATCH /api/auth/profile`; the registered phone number is intentionally read-only. OTP password reset/change UI is prepared for the next step and is currently disabled until an OTP provider is connected.

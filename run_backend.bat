@echo off
title backend startup
cd backend
python -m uvicorn app.main:app --reload --port 8000
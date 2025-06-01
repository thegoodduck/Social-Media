#!/bin/bash

tmux new-session -d -s pulse
tmux send-keys -t pulse "cd vidbackend/Pulse_Backend_Video/pulse && source ../../.venv/bin/activate && python manage.py runserver 0.0.0.0:8000" C-m
tmux split-window -h -t pulse
tmux send-keys -t pulse:0.1 "cd backend && npm run dev" C-m
tmux split-window -v -t pulse:0.1
tmux send-keys -t pulse:0.2 "cd frontend && npm run dev" C-m
tmux select-layout -t pulse even-horizontal
tmux attach -t pulse
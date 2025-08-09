"""
# dream_layer_backend/task_runner.py
# Author: Natalia Rodriguez Figueroa
# Email: natalia_rodriguezuc@berkeley.edu

# Task 2: Implement a matrix/grid image generation workflow. 
"""

import os
import json
import random
import logging
import itertools
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

import itertools
import json
import os

class MatrixRunner:
    def __init__(self, state_file="matrix_jobs.json"):
        self.state_file = state_file
        self.jobs = []
        self.index = 0
        self.paused = False
        self.load()

    # --- Core Job Management ---
    def generate(self, param_dict):
        """Create all jobs from parameter ranges and reset state"""
        keys = list(param_dict.keys())
        combos = list(itertools.product(*param_dict.values()))
        self.jobs = [
            {"id": i, **dict(zip(keys, combo)), "status": "pending"}
            for i, combo in enumerate(combos)
        ]
        self.index = 0
        self.paused = False
        self.save()

    def next_job(self):
        """Get the next pending job and mark it as running"""
        if self.paused:
            return None
        while self.index < len(self.jobs):
            job = self.jobs[self.index]
            self.index += 1
            if job["status"] == "pending":
                job["status"] = "running"
                self.save()
                return job
        return None  # No more jobs

    def complete_job(self, job_id):
        """Mark job as done"""
        for job in self.jobs:
            if job["id"] == job_id:
                job["status"] = "done"
                break
        self.save()

    # --- Pause / Resume ---
    def pause(self):
        self.paused = True
        self.save()

    def resume(self):
        self.paused = False
        self.save()

    # --- Persistence ---
    def save(self):
        with open(self.state_file, "w") as f:
            json.dump(
                {"jobs": self.jobs, "index": self.index, "paused": self.paused}, f, indent=2
            )

    def load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
            self.jobs = state.get("jobs", [])
            self.index = state.get("index", 0)
            self.paused = state.get("paused", False)

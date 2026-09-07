# Stage 1: Build Rust/CUDA bindings
FROM rust:latest as builder
WORKDIR /app
COPY . .

# Install dependencies for bindgen, PyO3, etc.
RUN apt-get update && apt-get install -y llvm-dev libclang-dev clang python3-dev

# Assuming CUDA 12.4 is available or using prebuilt LibTorch
# In a real environment we would download libtorch for tch-rs here
# ENV LIBTORCH=/path/to/libtorch

# Compile the PyO3 bridge
WORKDIR /app/antigravity_bridge
RUN cargo build --release

# Stage 2: Minimal FastAPI server
FROM python:3.11-slim

WORKDIR /app
# Install numpy and fastapi
RUN pip install numpy fastapi uvicorn datasets

# Copy compiled shared object and rename it to antigravity.so for Python import
COPY --from=builder /app/target/release/libantigravity.so /app/antigravity.so

# A minimal app exposing the simulation logic
COPY <<EOF /app/main.py
from fastapi import FastAPI
import numpy as np
import antigravity as ag

app = FastAPI()

@app.post("/simulate")
def simulate(dof: int = 168000, dataset: str = "huggingface/iter-m2n1"):
    # Initialize zero-copy numpy array state
    state = np.zeros(dof, dtype=np.float64)
    # Trigger PyO3 Rust Execution
    result = ag.simulate_disruption(dof, dataset, state)
    return {"status": "success", "message": result}
EOF

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

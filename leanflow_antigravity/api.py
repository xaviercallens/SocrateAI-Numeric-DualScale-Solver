from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import numpy as np
from leanflow_antigravity import workflow

app = FastAPI(title="LeanFlow Antigravity Serverless API")

# Preload a default small dataset for benchmarking the endpoint
try:
    default_state, default_dof = workflow.load_data(subset_dof=1000)
except FileNotFoundError:
    default_state = np.zeros(1000, dtype=np.float64)
    default_dof = 1000

class StepRequest(BaseModel):
    cycle_idx: int
    dt: float = 1e-3
    nu: float = 1e-3
    anisotropy_ratio: float = 1.0

@app.post("/step")
def step(request: StepRequest):
    try:
        # In a real scenario, the state would be passed or maintained.
        # For the stress test, we just execute on the preloaded state to test concurrency.
        record = workflow.execute_cycle_step(
            state=default_state,
            dof=default_dof,
            cycle_idx=request.cycle_idx,
            dt=request.dt,
            nu=request.nu,
            anisotropy_ratio=request.anisotropy_ratio
        )
        return {"status": "success", "record": record}
    except workflow.GaugeViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LeanFlow Antigravity - Web UI</title>
        <style>
            :root {
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-color: #f8fafc;
                --primary: #3b82f6;
                --primary-hover: #2563eb;
                --success: #10b981;
                --border: #334155;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 2rem;
                display: flex;
                justify-content: center;
            }
            .container {
                background-color: var(--card-bg);
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                width: 100%;
                max-width: 600px;
                border: 1px solid var(--border);
            }
            h1 {
                margin-top: 0;
                font-size: 1.5rem;
                border-bottom: 1px solid var(--border);
                padding-bottom: 1rem;
            }
            .form-group {
                margin-bottom: 1.5rem;
            }
            label {
                display: block;
                margin-bottom: 0.5rem;
                font-size: 0.875rem;
                color: #94a3b8;
            }
            input {
                width: 100%;
                padding: 0.75rem;
                background-color: var(--bg-color);
                border: 1px solid var(--border);
                color: var(--text-color);
                border-radius: 6px;
                box-sizing: border-box;
            }
            input:focus {
                outline: none;
                border-color: var(--primary);
            }
            button {
                background-color: var(--primary);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                font-size: 1rem;
                border-radius: 6px;
                cursor: pointer;
                width: 100%;
                font-weight: 600;
                transition: background-color 0.2s;
            }
            button:hover {
                background-color: var(--primary-hover);
            }
            button:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }
            #result {
                margin-top: 2rem;
                background-color: var(--bg-color);
                padding: 1rem;
                border-radius: 6px;
                border: 1px solid var(--border);
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 0.875rem;
                color: var(--success);
                display: none;
            }
            .error {
                color: #ef4444 !important;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LeanFlow Enterprise - API Tester</h1>
            <div class="form-group">
                <label for="cycle">Cycle Index</label>
                <input type="number" id="cycle" value="1">
            </div>
            <div class="form-group">
                <label for="dt">Time Step (dt)</label>
                <input type="number" id="dt" value="0.001" step="0.0001">
            </div>
            <div class="form-group">
                <label for="nu">Viscosity (nu)</label>
                <input type="number" id="nu" value="0.001" step="0.0001">
            </div>
            <div class="form-group">
                <label for="anisotropy">Anisotropy Ratio</label>
                <input type="number" id="anisotropy" value="1.0" step="0.1">
            </div>
            
            <button id="btn-submit" onclick="executeStep()">Execute Step</button>
            
            <div id="result"></div>
        </div>

        <script>
            async function executeStep() {
                const btn = document.getElementById('btn-submit');
                const resultDiv = document.getElementById('result');
                
                btn.innerText = "Executing...";
                btn.disabled = true;
                resultDiv.style.display = "none";
                resultDiv.className = "";
                
                const payload = {
                    cycle_idx: parseInt(document.getElementById('cycle').value),
                    dt: parseFloat(document.getElementById('dt').value),
                    nu: parseFloat(document.getElementById('nu').value),
                    anisotropy_ratio: parseFloat(document.getElementById('anisotropy').value)
                };

                try {
                    const response = await fetch('/step', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(payload)
                    });
                    
                    const data = await response.json();
                    
                    resultDiv.style.display = "block";
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                    
                    if (!response.ok) {
                        resultDiv.className = "error";
                    }
                } catch (error) {
                    resultDiv.style.display = "block";
                    resultDiv.className = "error";
                    resultDiv.textContent = "Network Error: " + error.message;
                } finally {
                    btn.innerText = "Execute Step";
                    btn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """

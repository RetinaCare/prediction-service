## Retina Care :: Prediction Service

This repository contains source code for our Flask API server that loads and predicts Diabetic Retinopathy progression given clinical features such as:

- HbA1c level (%)
- Duration (in years), and
- Systolic Blood Pressure (mmHg)

### Up and Running

1. Make sure you have Python, uv, and Docker installed on your development environment.
2. Git clone this repository.
3. Run the following commands:

   ```bash
   python3 -m venv .venv
   source ./.venv/bin/activate
   uv add -r requirements.txt
   ```
4. Once done, run the Flask app using this command:

   ```bash
   python3 ./api.py
   ```

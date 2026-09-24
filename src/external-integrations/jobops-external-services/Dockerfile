FROM python:3.12-slim
WORKDIR /app

COPY src/external-integrations/jobops-external-services/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY src/external-integrations/jobops-external-services ./
COPY config ./config
COPY resumes ./resumes

ENV PYTHONPATH=/app
ENV JOBOPS_CANDIDATE_PROFILE_PATH=/app/config/candidate/verified_profile.json
ENV JOBOPS_ANSWER_BANK_PATH=/app/config/candidate/answer_bank.json
ENV JOBOPS_RESUMES_DIR=/app/resumes

CMD ["python", "main.py"]

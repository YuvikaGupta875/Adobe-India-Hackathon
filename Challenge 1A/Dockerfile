# ----- Dockerfile (Round 1B ready) -----
    FROM --platform=linux/amd64 python:3.11-slim

    # deps
    RUN pip install --no-cache-dir \
            pdfminer.six==20221105 \
            scikit-learn==1.4.2 \
            numpy==1.26.4 \
            scipy==1.13.0
    
    # code
    WORKDIR /app
    COPY app ./app
    
    # default entrypoint = 1B analyser
    ENTRYPOINT ["python", "/app/app/analyser_1b.py", "/app/input"]
    
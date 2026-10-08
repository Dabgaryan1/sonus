from fastapi import FastAPI

app = FastAPI(title="Sonus API")

@app.get("/")
def root():
    return {"message": "Sonus is running"}
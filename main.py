from fastapi import FastAPI

app = FastAPI(title="To-Do List API")


@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to To-Do List API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # TODO: App initialization
    pass

@app.get("/health")
def health_check():
    return "OK"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
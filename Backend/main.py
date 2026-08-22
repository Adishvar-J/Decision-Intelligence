from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sympy import im
from ingest import Ingest
from data import Data
from chart_engine import Chart
from analytics import Analyzer



app = FastAPI()
ingest = Ingest()
analyzer = Analyzer()

chart = Chart()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hello world"}

@app.post("/upload")
async def upload_file(id: int, file: UploadFile = File(...)):
    file_bytes = await file.read()
    ingest.get_file(user_id=id, filename=file.filename, file_data=file_bytes)

    return {
        "user_id": id,
        "filename": file.filename,
        "size": len(file_bytes),
        "status": ingest.stat
    }

@app.get("/dashboard/{dset_id}")
def get_dashboard(dset_id: int):
    try:
        data = Data(user_id=dset_id)
        data.fetch().load().clean()
        data.normalize()
        data.validate()
        data_frame = data.transform()

        report = analyzer.analyze(data_frame)
        charts = chart.generate(data_frame)

        return {
            "user_id": dset_id,
            "analytics": report,
            "charts": charts
        }
    
    except Exception as e:
        return {
            "Internal Error": str(e)
        }
    
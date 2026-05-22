from fastapi import APIRouter

from app.services.data_loader import dataframe_to_records, load_cars, load_lanes


router = APIRouter(prefix="/api", tags=["data"])


@router.get("/cars")
def get_cars() -> dict:
    cars = load_cars()
    return {"data": dataframe_to_records(cars), "total": len(cars), "note": "模拟数据，非真实企业数据。"}


@router.get("/staging-lanes")
def get_staging_lanes() -> dict:
    lanes = load_lanes()
    return {"data": dataframe_to_records(lanes), "total": len(lanes), "note": "模拟备车道数据。"}

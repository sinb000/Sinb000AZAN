from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class Location(BaseModel):
    latitude: float
    longitude: float
    city: Optional[str] = None

class PrayerAdjustments(BaseModel):
    fajr: int = 0
    dhuhr: int = 0
    asr: int = 0
    maghrib: int = 0
    isha: int = 0

class SilentMode(BaseModel):
    fajr: bool = False
    dhuhr: bool = False
    asr: bool = False
    maghrib: bool = False
    isha: bool = False

class PrayerSettings(BaseModel):
    user_id: str
    location: Optional[Location] = None
    useGPS: bool = True
    adjustments: PrayerAdjustments = Field(default_factory=PrayerAdjustments)
    silentMode: SilentMode = Field(default_factory=SilentMode)
    audioSource: str = "radio"  # "radio", "local", or "custom"
    customAudioUri: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PrayerSettingsCreate(BaseModel):
    user_id: str
    location: Optional[Location] = None
    useGPS: bool = True
    adjustments: Optional[PrayerAdjustments] = None
    silentMode: Optional[SilentMode] = None
    audioSource: str = "radio"
    customAudioUri: Optional[str] = None


# Prayer Settings Routes
@api_router.post("/prayer-settings", response_model=PrayerSettings)
async def save_prayer_settings(settings: PrayerSettingsCreate):
    """حفظ أو تحديث إعدادات الصلاة للمستخدم"""
    settings_dict = settings.dict()
    settings_dict['updated_at'] = datetime.utcnow()
    
    # البحث عن إعدادات المستخدم الحالية
    existing = await db.prayer_settings.find_one({"user_id": settings.user_id})
    
    if existing:
        # تحديث الإعدادات الموجودة
        await db.prayer_settings.update_one(
            {"user_id": settings.user_id},
            {"$set": settings_dict}
        )
    else:
        # إنشاء إعدادات جديدة
        await db.prayer_settings.insert_one(settings_dict)
    
    updated_settings = await db.prayer_settings.find_one({"user_id": settings.user_id})
    return PrayerSettings(**updated_settings)

@api_router.get("/prayer-settings/{user_id}", response_model=PrayerSettings)
async def get_prayer_settings(user_id: str):
    """الحصول على إعدادات الصلاة للمستخدم"""
    settings = await db.prayer_settings.find_one({"user_id": user_id})
    
    if not settings:
        raise HTTPException(status_code=404, detail="إعدادات المستخدم غير موجودة")
    
    return PrayerSettings(**settings)

@api_router.get("/")
async def root():
    return {"message": "تطبيق الأذان API"}


# ===== نظام المنبهات =====

class AlarmDate(BaseModel):
    date: str  # ISO date string
    time: str  # HH:MM

class AlarmRepeat(BaseModel):
    type: str = "none"
    interval: int = 1
    unit: str = "day"
    weekdays: List[str] = []
    monthDays: List[int] = []
    yearlyMonth: int = 1
    yearlyDay: int = 1

class AlarmCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sound_uri: Optional[str] = None
    sound_name: Optional[str] = None
    repeat: AlarmRepeat = Field(default_factory=AlarmRepeat)
    dates: List[AlarmDate] = []
    default_time: str = "08:00"
    enabled: bool = True

class Alarm(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    sound_uri: Optional[str] = None
    sound_name: Optional[str] = None
    repeat: AlarmRepeat = Field(default_factory=AlarmRepeat)
    dates: List[AlarmDate] = []
    enabled: bool = True
    created_at: str = ""

@api_router.post("/alarms")
async def create_alarm(alarm: AlarmCreate):
    alarm_dict = alarm.dict()
    alarm_dict['id'] = str(uuid.uuid4())
    alarm_dict['created_at'] = datetime.utcnow().isoformat()
    await db.alarms.insert_one(alarm_dict)
    alarm_dict.pop('_id', None)
    return alarm_dict

@api_router.get("/alarms")
async def get_alarms():
    alarms = await db.alarms.find({}, {"_id": 0}).to_list(100)
    return alarms

@api_router.put("/alarms/{alarm_id}")
async def update_alarm(alarm_id: str, alarm: AlarmCreate):
    alarm_dict = alarm.dict()
    result = await db.alarms.update_one({"id": alarm_id}, {"$set": alarm_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="المنبه غير موجود")
    updated = await db.alarms.find_one({"id": alarm_id}, {"_id": 0})
    return updated

@api_router.patch("/alarms/{alarm_id}/toggle")
async def toggle_alarm(alarm_id: str):
    alarm = await db.alarms.find_one({"id": alarm_id})
    if not alarm:
        raise HTTPException(status_code=404, detail="المنبه غير موجود")
    new_state = not alarm.get('enabled', True)
    await db.alarms.update_one({"id": alarm_id}, {"$set": {"enabled": new_state}})
    return {"id": alarm_id, "enabled": new_state}

@api_router.delete("/alarms/{alarm_id}")
async def delete_alarm(alarm_id: str):
    result = await db.alarms.delete_one({"id": alarm_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="المنبه غير موجود")
    return {"message": "تم حذف المنبه"}

# بث إذاعة القرآن الكريم عبر proxy (HTTPS)
RADIO_STREAM_URL = "http://live.mp3quran.net:8002/stream"

@api_router.get("/radio-stream")
async def radio_stream():
    """بث إذاعة القرآن الكريم كـ proxy"""
    async def stream_generator():
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", RADIO_STREAM_URL, timeout=None) as response:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    yield chunk

    return StreamingResponse(
        stream_generator(),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Accept-Ranges": "none",
        }
    )

from fastapi.responses import FileResponse

@api_router.get("/adhan-file")
async def get_adhan_file():
    """تحميل ملف الأذان الافتراضي"""
    adhan_path = ROOT_DIR / "adhan.mp3"
    if not adhan_path.exists():
        raise HTTPException(status_code=404, detail="ملف الأذان غير موجود")
    return FileResponse(str(adhan_path), media_type="audio/mpeg", filename="adhan.mp3")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

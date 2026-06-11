from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Automated OSINT API", version="1.0.0")

# إعداد CORS للسماح للواجهة الأمامية بالاتصال
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # في الإنتاج يجب تحديد النطاق بدلاً من *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "OSINT API is running!"}

from analyzer import analyze_target
from database import init_db, save_scan, get_history, get_scan_by_id
from fastapi import HTTPException

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db()

from fastapi import Request

@app.get("/api/scan")
def scan_target(target: str, request: Request):
    # استخراج مفاتيح API من ترويسات الطلب (إن وجدت)
    hunter_key = request.headers.get('x-hunter-key', '')
    hibp_key = request.headers.get('x-hibp-key', '')
    
    api_keys = {
        "hunter": hunter_key if hunter_key else None,
        "hibp": hibp_key if hibp_key else None
    }
    
    # تشغيل التحليل وتمرير المفاتيح
    results = analyze_target(target, api_keys)
    
    # حفظ النتيجة في قاعدة البيانات
    if results and "raw_data" in results and "nodes" in results:
        graph_data = {"nodes": results["nodes"], "edges": results["edges"]}
        save_scan(target, results["raw_data"], graph_data)
        
    return results

@app.get("/api/history")
def get_scan_history():
    return get_history()

@app.get("/api/history/{scan_id}")
def get_scan_details(scan_id: int):
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # تحويل البيانات إلى الشكل الذي يتوقعه الواجهة الأمامية
    return {
        "raw_data": scan["raw_data"],
        "nodes": scan["graph_data"]["nodes"],
        "edges": scan["graph_data"]["edges"],
        "target": scan["target"],
        "scan_date": scan["scan_date"]
    }

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# إعداد لخدمة الواجهة الأمامية من نفس خادم FastAPI
dist_path = os.path.join(os.path.dirname(__file__), "dist")

if os.path.isdir(dist_path):
    # خدمة الملفات الثابتة (JS, CSS, Images)
    assets_path = os.path.join(dist_path, "assets")
    if os.path.isdir(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
        
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        # منع اعتراض طلبات الـ API
        if catchall.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
            
        file_path = os.path.join(dist_path, catchall)
        # إذا كان الملف موجوداً (مثل vite.svg) قم بخدمته
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # غير ذلك، قدم index.html ليدير React مساراته (React Router)
        return FileResponse(os.path.join(dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

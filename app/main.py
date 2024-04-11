import models, uvicorn
from database import engine
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from routers import ai, control, addData, watchVisit, update, analyze, account, download, patientManage
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import FileResponse


if __name__ == "__main__": #便捷啟動, 於Windows環境輸入py main.py可啟用 
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, log_level="info")
    # 於遠端主機操作時不可用0.0.0.0與port=8000(因為此ip預設對外廣播)與, 另設置一種於下方註解
    # config = uvicorn.Config("main:app", host="127.0.0.1", port=8181, log_level="info")
    server = uvicorn.Server(config)
    server.run()

models.Base.metadata.create_all(bind=engine)  #資料庫功能

app = FastAPI()  #app為instance(object), FastAPI為class, 白話而言就是啟動網頁所需的指涉主體

app.mount("/static", StaticFiles(directory="./static"), name="static")  #靜態資料(例如css)夾指定
app.mount("/ai", StaticFiles(directory="./ai"), name="ai")  #靜態資料(例如css)夾指定

@app.middleware("http")  #session功能啟用
async def validate_user(request: Request, call_next):
    response = await call_next(request)
    return response

#利用結構化程式設計概念去做功能導引
app.include_router(control.router)  #病歷管理相關(登入, 個人設置, 連結新增與查看功能的中控台)
app.include_router(addData.router)  #新增就診相關(初診、複診)
app.include_router(patientManage.router)  #管理病歷相關(病歷資料)
app.include_router(watchVisit.router)  #管理(查看)病歷相關
app.include_router(update.router)  #修改病歷
app.include_router(analyze.router) #分析病歷相關
app.include_router(account.router) #帳號相關
app.include_router(ai.router) #ai醫療輔助建模
app.include_router(download.router) #下載病歷


# 首頁導引
@app.get("/", response_class=RedirectResponse)
def index():
    return "/login"

#session功能對應@app.middleware("http"), 必須放最尾
app.add_middleware(SessionMiddleware, secret_key="some-random-string")
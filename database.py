from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import sqlalchemy as sa




# connection_string = "DRIVER={SQL Server Native Client 11.0};SERVER=172.23.128.1;DATABASE=STANDUPDEVELOP;UID=sa;PWD=standup" #遠端主機
# connection_string = "DRIVER={SQL Server Native Client 11.0};SERVER=DESKTOP-IFISBUA\standup;DATABASE=STANDUPDEVELOP;UID=sa;PWD=standup" #遠端主機
# connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=172.23.128.1;DATABASE=STANDUPDEVELOP;TrustServerCertificate=yes;UID=sa;PWD=StandUp@0123;"
connection_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=DESKTOP-IFISBUA\standup;DATABASE=STANDUPDEVELOP;TrustServerCertificate=yes;UID=sa;PWD=standup;"
# engine = create_engine("mssql+pyodbc://sa:standup@DESKTOP-IFISUBA:1433/STANDUPDEVELOP?driver=ODBC+Driver+18+for+SQL+Server")
# connection_string = "DRIVER={SQL Server Native Client 11.0};SERVER=LAPTOP-H25R8F0D\standup;DATABASE=STANDUPDEVELOP;UID=sa;PWD=standup" #冠霖的筆電
# connection_string = "DRIVER={SQL Server Native Client 11.0};SERVER=DESKTOP-Q2H2DEH6\STANDUP;DATABASE=standup;UID=sa;PWD=standup" #欣的筆電
# connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string}) #sqlserver資料庫連線資料驗證字串

import urllib
engine = create_engine('mssql+pyodbc:///?odbc_connect=' + urllib.parse.quote_plus(connection_string))
# engine = create_engine('mssql+pyodbc://sa:standup@DESKTOP-IFISBUA/STANDUPDEVELOP?driver=SQL+Server+Native+Client+11.0')
# engine = create_engine(connection_string) #創建一個database的pool(想像成可透過此快速連接)並作為啟用點

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #啟用database的session來操作

Base = declarative_base() #創建資料庫table與相關column前所需的基底(利用ORM, 類似物件導向技術來映射), 會import進models.py

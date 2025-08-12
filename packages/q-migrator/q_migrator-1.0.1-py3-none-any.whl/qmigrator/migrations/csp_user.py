import typer
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, Field
from migrations.utils import excel_row_generator, validate_empty_str, error_log, success_log, info_log


class EXCEL_CSP_USER(BaseModel):
    userid: int = Field(..., alias="USERID")
    name: str = Field(..., alias="NAME")
    companyid: int = Field(..., alias="COMPANYID")
    csp_sync_version: int = Field(..., alias="CSP_SYNC_VERSION")
    jobrsp_year_nm: str | None = Field(None, alias="JOBRSP_YEAR_NM")
    grade_year_nm: str | None = Field(None, alias="GRADE_YEAR_NM")
    job_nm: str | None = Field(None, alias="JOB_NM")
    grade_nm: str | None = Field(None, alias="GRADE_NM")
    createtime: datetime = Field(..., alias="CREATETIME")
    creater: str | None = Field(None, alias="CREATER")
    login_id: str = Field(..., alias="LOGIN_ID")


def migrate_csp_user(session: Session, excel_path: str, batch_size: int = 100):
    data: list[EXCEL_CSP_USER] = []
    
    for i, row in enumerate(excel_row_generator(excel_path)):
        error_data = validate_empty_str(row, i + 1)
        
        if len(error_data) != 0:
            error_log(f"빈 문자열이 포함된 데이터")
            for err in error_data:
                error_log(f"\t- row_num: {err['row_num']}, col_num: {err['col_num']}, Key: {err['key']}")
            typer.Exit(1)
        
        try:
            data.append(EXCEL_CSP_USER(**row))
        except Exception as e:
            error_log(f"데이터 무결성 검증 실패 - {e}")
            typer.Exit(1)
    
    select_sql = text("""SELECT COUNT(*) FROM TB_CSP_USER""")
    
    insert_sql = text("""
        INSERT INTO TB_CSP_USER (
            USERID, NAME, JOBRSP_YEAR_NM, 
            GRADE_YEAR_NM, JOB_NM, GRADE_NM, 
            CREATETIME, CREATER, COMPANYID, 
            CSP_SYNC_VERSION, LOGIN_ID
        )
        VALUES (
            :USERID, :NAME, :JOBRSP_YEAR_NM,
            :GRADE_YEAR_NM, :JOB_NM, :GRADE_NM,
            :CREATETIME, :CREATER, :COMPANYID,
            :CSP_SYNC_VERSION, :LOGIN_ID
        )
    """)
    
    select_result = session.execute(select_sql).scalar_one()
    
    if select_result > 0:
        error_log("대상 테이블이 비어있지 않습니다.")
        typer.Exit(1)
    
    # 100개씩 Bulk Insert
    step = batch_size
    total_len = len(data)
    
    try:
        for i in range(0, total_len, step):
            start = i
            end = i + step if i + step < total_len else total_len
            users = data[start:end]
            
            data_to_insert = [{
                'USERID': user.userid,
                'NAME': user.name,
                'JOBRSP_YEAR_NM': user.jobrsp_year_nm,
                'GRADE_YEAR_NM': user.grade_year_nm,
                'JOB_NM': user.job_nm,
                'GRADE_NM': user.grade_nm,
                'CREATETIME': user.createtime,
                'CREATER': user.creater,
                'COMPANYID': user.companyid,
                'CSP_SYNC_VERSION': user.csp_sync_version,
                'LOGIN_ID': user.login_id
            } for user in users]

            session.execute(insert_sql, data_to_insert)
            info_log(f"[{end}/{total_len}] INSERTING CSP_USER")
        
        session.commit()
        success_log(f"{total_len}개 데이터 마이그레이션 완료")
            
    except Exception as e:
        session.rollback()
        error_log(f"데이터 삽입 과정에서 에러 발생: {e}")
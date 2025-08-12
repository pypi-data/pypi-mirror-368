import typer 
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from migrations.csp_user import migrate_csp_user

app = typer.Typer(help="Cufit-C 데이터 마이그레이션을 위한 CLI 도구")

@app.command()
def migrate(
    target: str = typer.Option(..., "--migrate", "-m", help="마이그레이션 대상 지정"),
    db_url: str = typer.Option(..., help="마이그레이션 대상 DB URL"),
    excel_path: str = typer.Option(..., help="마이그레이션 대상 엑셀 파일 경로"),
    batch_size: int = typer.Option(100, help="배치 INSERT 레코드 수")
):
    # DB 접속 및 Excel 경로 검증 
    if not Path(excel_path).exists():
        typer.echo(f"[ERROR] 엑셀 파일 경로가 유효하지 않습니다.")
    
    try:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
    except Exception:
        typer.echo("[ERROR] DB 접속 에러", fg=typer.colors.RED)
        typer.Exit(1)
    
    with Session() as session:
        if target == "user":
            migrate_csp_user(session, excel_path, batch_size)
        else:
            typer.echo(f"[ERROR] 지원하지 않는 대상: {target}", fg=typer.colors.RED)

def main():
    app()

if __name__ == "__main__":
    main()
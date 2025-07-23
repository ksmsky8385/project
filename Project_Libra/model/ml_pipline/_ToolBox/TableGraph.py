import os, sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import matplotlib.font_manager as fm

# 한글 폰트 설정 (Windows 기준)
font_path = "C:/Windows/Fonts/malgun.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams["font.family"] = font_prop.get_name()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_utiles.OracleDBConnection import OracleDBConnection
from core_utiles.config_loader import BASE_OUTPUT_DIR

warnings.filterwarnings("ignore")
sns.set(style="whitegrid")

def fetch_table(table_name):
    connector = OracleDBConnection()
    connector.connect()
    query = f"SELECT * FROM {table_name}"
    try:
        df = pd.read_sql(query, con=connector.engine)
        df.columns = df.columns.str.strip().str.upper()
    except Exception as e:
        print("[오류] 테이블 조회 실패:", e)
        df = pd.DataFrame()
    connector.close()
    return df

def plot_sorted_feature(df, feature, mode="all", count=None, save=False, save_path=None, filename=None):
    feature_upper = feature.strip().upper()
    if feature_upper not in df.columns:
        print(f"[오류] 피처 '{feature}'가 테이블에 존재하지 않습니다.")
        print("→ 실제 컬럼 목록:", df.columns.tolist())
        return

    
    # df_sorted = df.sort_values(by="SCR", ascending=True)
    df_sorted = df.sort_values(by=["YR", "SCR"], ascending=[True, True])
    
    if mode == "top" and count:
        df_sorted = df_sorted.tail(count)
    elif mode == "bottom" and count:
        df_sorted = df_sorted.head(count)

    df_sorted["SNM_LABEL"] = df_sorted["SNM"] + " (" + df_sorted["YR"].astype(str) + ")" + " (" + df_sorted["SCR"].astype(str) + ")"
    num_rows = len(df_sorted)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="SNM_LABEL", y=feature_upper, data=df_sorted, palette="viridis", ax=ax)

    ax.set_title(f"[{feature}] vs 대학 이름 (SCR 기준 오름차순)", fontproperties=font_prop)
    ax.set_xlabel("대학교 (개별 행)", fontproperties=font_prop)
    ax.set_ylabel(feature, fontproperties=font_prop)

    for label in ax.get_xticklabels():
        label.set_fontproperties(font_prop)
        label.set_rotation(90)

    fig.subplots_adjust(bottom=0.35)
    fig.text(0.5, 0.05, f"데이터 행 수: {num_rows}개", ha="center", fontproperties=font_prop)

    if save and save_path:
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, filename or f"{feature}_sorted_barplot.png")
        plt.savefig(file_path)
        print(f"[저장 완료] → {file_path}")

    plt.show()

if __name__ == "__main__":
    TABLE_NAME  = "LIBRA.FILTERED"
    # feature = "SCR"           # 점수
    # feature = "APS_APS"       # 재학생 1인당 도서관건물 연면적
    # feature = "BGT_MCT"       # 예산_자료구입비계
    # feature = "BGT_UBGT"      # 예산_대학총예산
    # feature = "BPS_BPS"       # 재학생 1인당 소장도서수
    # feature = "BR_BCNT_SUM"   # 도서자료_책수_계
    # feature = "CPSS_CPS"      # 재학생 1인당 자료구입비(결산)
    # feature = "EHS_EHS"       # 직원 1인당 평균 교육 참여 시간
    # feature = "FACLT_EQP_TPC" # 시설설비정보화기기(PC)수
    # feature = "FACLT_LAS"     # 시설_도서관건물연면적 (제곱미터)
    # feature = "FACLT_RS_TRS"  # 시설_열람석_총열람석수
    # feature = "LBRT_USTL"     # 대학총결산 대비 도서관 자료구입비 비율
    # feature = "LPK_LPK"       # 재학생 1,000명당 사서 직원수
    # feature = "LPS_LPS"       # 재학생 1인당 대출책수
    # feature = "LS_LB_SUM"     # 대출현황_대출책수_계
    # feature = "LS_LU_SUM"     # 대출현황_대출자수_계
    # feature = "SPK_SPK"       # 재학생 1,000명당 도서관 직원수
    # feature = "STL_MCT"       # 결산_자료구입비계
    # feature = "STL_USTL"      # 결산_대학총결산
    feature = "VPS_VPS"       # 재학생 1인당 도서관방문자수
    # feature = "VUC_UC_LUC"    # 봉사대상자수 및 이용자수_도서관 이용자수

    mode        = "all"
    count       = None
    save_option = True
    save_path   = "D:/workspace/project/KG_AI_Project/resource"
    filename    = f"그래프({TABLE_NAME}-{feature}).png"

    df = fetch_table(TABLE_NAME)
    if df.empty:
        print("[데이터 없음] 테이블 불러오기 실패")
    else:
        plot_sorted_feature(
            df,
            feature=feature,
            mode=mode,
            count=count,
            save=save_option,
            save_path=save_path,
            filename=filename
        )

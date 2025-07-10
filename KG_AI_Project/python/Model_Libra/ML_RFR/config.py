# 입력 컬럼 및 예측 타깃 정의

'''

원래 컬럼명 ->	변환된 한글 컬럼명

APS_APS	        재학생 1인당 도서관건물 연면적_재학생 1인당 도서관건물 연면적
BGT_MCT	        예산_자료구입비계
BGT_UBGT	    예산_대학총예산
BPS_BPS	        재학생 1인당 소장도서수_재학생 1인당 소장도서수
BR_BCNT_SUM	    도서자료_책수_계
CPSS_CPS	    재학생 1인당 자료구입비(결산)_재학생 1인당 자료구입비
EHS_EHS	        직원 1인당 평균 교육 참여 시간_직원 1인당 평균 교육 참여 시간
FACLT_EQP_TPC	시설설비정보화기기(PC)수
FACLT_LAS	    시설_도서관건물연면적 (제곱미터)
FACLT_RS_TRS	시설_열람석_총열람석수
LBRT_USTL	    대학총결산 대비 도서관 자료구입비 비율_대학총결산
LPK_LPK	        재학생 1,000명당 사서 직원수_재학생 1,000명당 사서 직원수
LPS_LPS	        재학생 1인당 대출책수_재학생 1인당 대출책수
LS_LB_SUM	    대출현황_대출책수_계
LS_LU_SUM	    대출현황_대출자수_계
SPK_SPK	        재학생 1,000명당 도서관 직원수_재학생 1,000명당 도서관 직원수
STL_MCT	        결산_자료구입비계
STL_USTL	    결산_대학총결산
VPS_VPS	        재학생 1인당 도서관방문자수_재학생 1인당 도서관방문자수
VUC_UC_LUC	    봉사대상자수 및 이용자수_이용자수_도서관 이용자수


'''




INPUT_COLUMNS = [
    "APS_APS", "BGT_MCT", "BGT_UBGT", "BPS_BPS", "BR_BCNT_SUM",
    "CPSS_CPS", "EHS_EHS", "FACLT_EQP_TPC", "FACLT_LAS", "FACLT_RS_TRS",
    "LBRT_USTL", "LPK_LPK", "LPS_LPS", "LS_LB_SUM", "LS_LU_SUM",
    "SPK_SPK", "STL_MCT", "STL_USTL", "VPS_VPS", "VUC_UC_LUC"
    ]
TARGET_COLUMN = "SCR"
FILTERED_TABLE = "LIBRA.FILTERED"

# RFR 하이퍼파라미터
RFR_PARAMS = {
    "n_estimators": 500,
    "max_depth": 15,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "max_features": "sqrt",
    "random_state": 42,
    "n_jobs": -1
}


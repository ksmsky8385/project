import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import statistics

class TunerLogRanker:
    def __init__(self, log_path: Path, output_path: Path):
        self.log_path = log_path
        self.output_path = output_path

    def _load_log(self) -> List[Dict[str, Any]]:
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[경고] 로그 파일을 찾거나 불러올 수 없습니다: {self.log_path}")
            return []

    def rank_top_trials(self, top_k: int = 10):
        logs = self._load_log()
        if not logs:
            print("[실패] 로그가 비어있거나 로드되지 않았습니다.")
            return

        # 클러스터별 R² 집계 및 횟수 카운트
        r2_map = defaultdict(list)
        cluster_count = defaultdict(int)

        for trial in logs:
            n_clusters = trial.get("n_clusters")
            cluster_r2 = trial.get("summary_metrics", {}).get("cluster_test", {}).get("R2", None)
            full_r2 = trial.get("summary_metrics", {}).get("full_predict", {}).get("R2", None)

            # 조건 필터링: 클러스터와 full R²가 모두 0.8 이상인 경우만 포함
            if (cluster_r2 is not None and full_r2 is not None and
                cluster_r2 >= 0.8 and full_r2 >= 0.8 and n_clusters is not None):
                r2_map[n_clusters].append(cluster_r2)
                cluster_count[n_clusters] += 1
            else:
                continue  # 조건 미달 trial은 제외

        # 평균 + 횟수 붙여서 문자열화
        average_r2_by_nclusters = {
            str(k): f"{round(statistics.mean(r2_map[k]), 4)} (n={cluster_count[k]})"
            for k in sorted(r2_map.keys())
        }

        # 필터링된 trial 재추출
        filtered_trials = [
            trial for trial in logs
            if trial.get("summary_metrics", {}).get("cluster_test", {}).get("R2", -1) >= 0.8 and
                trial.get("summary_metrics", {}).get("full_predict", {}).get("R2", -1) >= 0.8
        ]

        if not filtered_trials:
            print("[실패] 조건을 만족하는 trial이 없습니다.")
            return

        # 복합 정렬 기준
        def sort_key(trial: Dict[str, Any]):
            stddev_mean = trial.get("mean_rank_stddev", float("inf"))
            error_score = trial.get("rank_error_score", float("inf"))
            summary = trial.get("summary_metrics", {})

            cluster_r2 = summary.get("cluster_test", {}).get("R2", -999)
            full_r2 = summary.get("full_predict", {}).get("R2", -999)
            cluster_better = 1 if cluster_r2 > full_r2 else 0

            return (
                stddev_mean,             # 평균 표준편차 낮은 순
                error_score,             # 오차점수 낮은 순
                -cluster_r2,             # 클러스터 R2 높은 순
                -cluster_better,         # 클러스터가 full보다 높은 경우 우선
                -full_r2                 # full R2 높은 순
            )

        # 랭킹 대상 trial 정렬 및 추출
        sorted_trials = sorted(filtered_trials, key=lambda x: sort_key(x))[:top_k]

        ranked = []
        for idx, trial in enumerate(sorted_trials, start=1):
            summary = trial.get("summary_metrics", {})
            cluster_r2 = summary.get("cluster_test", {}).get("R2", -999)
            full_predict_r2 = summary.get("full_predict", {}).get("R2", -999)

            ranked.append({
                "rank": idx,
                "timestamp": trial.get("timestamp"),
                "n_clusters": trial.get("n_clusters"),
                "score_keys": {
                    "mean_rank_stddev": trial.get("mean_rank_stddev"),
                    "rank_error_score": trial.get("rank_error_score"),
                    "rank_stddev_by_year": trial.get("rank_stddev_by_year", {}),
                    "rank_error_by_year": trial.get("rank_error_by_year", {}),
                    "cluster_R2": cluster_r2,
                    "full_predict_R2": full_predict_r2,
                    "cluster_better_than_predict": cluster_r2 > full_predict_r2
                },
                "cluster_params": trial.get("cluster_params"),
                "summary_metrics": summary
            })

        output = {
            "average_R2_by_n_clusters": average_r2_by_nclusters,
            "ranked_trials": ranked
        }

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"[완료] 조건을 만족한 trial 중 Top {top_k} 랭킹 추출 완료 → {self.output_path}")


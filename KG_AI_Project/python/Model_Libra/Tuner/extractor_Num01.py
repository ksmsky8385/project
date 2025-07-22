import json
import os

class Num01Extractor:
    def __init__(self, filepath, save_dir=None,
                min_cluster_r2=0.8, prioritize_cluster_better=True):
        self.filepath = filepath
        self.save_dir = save_dir or os.path.dirname(filepath)
        self.min_cluster_r2 = min_cluster_r2
        self.prioritize_cluster_better = prioritize_cluster_better

    def load_logs(self):
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def filter_and_rank(self, logs):
        # 조건 필터링
        filtered = [
            log for log in logs
            if log.get("cluster_R2", 0) >= self.min_cluster_r2
            and (not self.prioritize_cluster_better or log.get("cluster_better_than_predict"))
        ]

        # 정렬 기준: mean_rank_stddev, cluster_R2, cluster_better_than_predict=True 우선, full_predict_R2
        ranked = sorted(filtered, key=lambda x: (
            x.get("mean_rank_stddev", float("inf")),
            -x.get("cluster_R2", 0),
            not x.get("cluster_better_than_predict", False),
            -x.get("full_predict_R2", 0)
        ))
        return ranked

    def extract_top_n(self, n=3):
        logs = self.load_logs()
        ranked_logs = self.filter_and_rank(logs)
        top_n = ranked_logs[:n]
        save_path = os.path.join(self.save_dir, "Num01_extraction.json")
        with open(save_path, "w") as f:
            json.dump(top_n, f, indent=2)
        print(f"추출된 {len(top_n)}개 항목을 저장: {save_path}")
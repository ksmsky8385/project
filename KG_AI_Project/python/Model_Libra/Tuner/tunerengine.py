import random

class RandomTuner:
    def __init__(self, param_spec: dict):
        self.param_spec = param_spec
        self.sampled_history = set()

    def sample_param(self, spec: dict):
        if spec["type"] == "fixed":
            return spec["fixed"]
        elif spec["type"] == "categorical":
            choice = random.choice(spec.get("choices", []))
            return None if choice in [None, "None", "null"] else choice
        elif spec["type"] == "int":
            low, high = spec["range"]
            return random.randint(low, high)
        elif spec["type"] == "float":
            low, high = spec["range"]
            return round(random.uniform(low, high), 4)
        return None

    def sample_single_model_params(self) -> dict:
        sampled = {}
        for key, spec in self.param_spec.items():
            if key == "n_clusters":
                continue  # 클러스터 수는 별도로 다룸
            val = self.sample_param(spec)
            if val is not None:
                sampled[key] = val
        return sampled

    def sample_params(self) -> dict:
        for _ in range(10):
            result = {}

            # 클러스터 수 먼저 샘플링
            cluster_spec = self.param_spec.get("n_clusters", {"type": "int", "range": [2, 5]})
            n_clusters = self.sample_param(cluster_spec)
            result["n_clusters"] = n_clusters

            # 풀 모델 하이퍼파라미터
            full_params = self.sample_single_model_params()
            result["full"] = full_params

            # 클러스터별 하이퍼파라미터
            for i in range(n_clusters):
                cluster_params = self.sample_single_model_params()
                result[str(i)] = cluster_params

            # 중복 방지 처리
            hashable = frozenset((key, frozenset(value.items())) for key, value in result.items() if isinstance(value, dict))
            if hashable not in self.sampled_history:
                self.sampled_history.add(hashable)
                return result

        return result

from mlguardian.monitored_model import MonitoredModel
from mlguardian.decorators import monitor_function

class DummyModel:
    def predict(self, X):
        return [0]*len(X)

def test_monitor_decorator(monkeypatch):
    posts = []
    def fake_post(url, json, headers=None, timeout=None):
        posts.append(json)
        class R:
            status_code = 200
            text = ""
        return R()
    monkeypatch.setattr("requests.post", fake_post)

    mm = MonitoredModel(DummyModel(), api_url="http://localhost:8001", model_name="dec", sample_rate=1.0)

    @monitor_function(mm, "fn")
    def f(x):
        return x+1

    assert f(1) == 2
    mm.flush(2.0)
    mm.stop()
    assert len(posts) >= 1

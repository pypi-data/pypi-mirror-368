import time
from mlguardian.monitored_model import MonitoredModel

class DummyModel:
    def predict(self, X):
        time.sleep(0.001)
        return [0] * (len(X) if hasattr(X, "__len__") else 1)

def test_predict_enqueues(monkeypatch):
    sent = []
    def fake_post(url, json, headers=None, timeout=None):
        sent.append((url, json))
        class R:
            status_code = 200
            text = ""
        return R()
    monkeypatch.setattr("requests.post", fake_post)

    dummy = DummyModel()
    mm = MonitoredModel(dummy, api_url="http://localhost:8001", model_name="d1", sample_rate=1.0)
    res = mm.predict([1,2,3])
    assert len(res) == 3
    mm.flush(2.0)
    mm.stop()
    assert len(sent) >= 1

import os
import urllib.request
import pickle

TARGET_DIR = '/opt/flink-job'

# create target dir if missing (host bind may create it)
os.makedirs(TARGET_DIR, exist_ok=True)

# 1) try multiple possible Maven coordinates for the Flink Kafka connector
JAR_PATH = os.path.join(TARGET_DIR, 'flink-connector-kafka.jar')
if not os.path.exists(JAR_PATH):
    print('Attempting to download Kafka connector jar to', JAR_PATH)
    candidates = []
    versions = ['1.17.5','1.17.4','1.17.3','1.17.2','1.17.1','1.17.0']
    scalas = ['2.12','2.13']
    for v in versions:
        for s in scalas:
            fname = f'flink-connector-kafka_{s}-{v}.jar'
            url = f'https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka_{s}/{v}/{fname}'
            candidates.append(url)

    downloaded = False
    for url in candidates:
        try:
            print('Trying', url)
            urllib.request.urlretrieve(url, JAR_PATH)
            print('Downloaded connector jar from', url)
            downloaded = True
            break
        except Exception as e:
            print('Failed to download from', url, ':', e)

    if not downloaded:
        print('Could not download any candidate connector jar. You can manually place the appropriate jar as', JAR_PATH)
else:
    print('Connector jar already present')

# 2) create a tiny dummy model.pkl with a predict method (no external deps)
MODEL_PATH = os.path.join(TARGET_DIR, 'model.pkl')

if not os.path.exists(MODEL_PATH):
    print('Creating dummy model at', MODEL_PATH)
    class DummyModel:
        def predict(self, X):
            # always predict 0 for any input
            return [0 for _ in X]

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(DummyModel(), f)
    print('Dummy model created')
else:
    print('Model already present')

print('init_flink_job finished')

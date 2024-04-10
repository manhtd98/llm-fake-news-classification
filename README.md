### Load elastic cluster
```
cd elasticsearch-cluster
docker-compose up -d
```

### Run streamlit app
```
cd elasticsearch-vector-store
pip3 install -r requirements.txt
streamlit run app.py 
```

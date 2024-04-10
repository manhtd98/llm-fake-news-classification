
### Query document

```
curl -X 'POST' \
  'http://localhost:80/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "query":"What is IOTA?",
    "topk":5
}'
```
```
ct2-transformers-converter --model vinai/PhoWhisper-large --output_dir whisper-large-v3 --copy_files tokenizer.json preprocessor_config.json --quantization float16

````

```
docker build -t streamlit-docker .
cd ..
sudo docker run --rm --gpus all --network="host" -v $(pwd)/elasticsearch-vector-store:/app  -v $(pwd)/models:/app/models --env-file elasticsearch-vector-store/.env streamlit-docker streamlit run app.py --server.fileWatcherType none
```

```
# export PYENV_ROOT="$HOME/.pyenv"
# [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
# eval "$(pyenv init -)"

# python3.10 -m pip install --upgrade setuptools wheel


# export CUDA_HOME=/usr/local/cuda-12.2
# export PATH=${CUDA_HOME}/bin:${PATH}
# export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:$LD_LIBRARY_PATH

# update gcc-+11 g++-11 
# nvcc 12.4
# uninstall nvidia-tool-kit

# CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip3 install --upgrade --force-reinstall llama-cpp-python

# python3.10 -m pip install -r requirements.txt
# CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 python3.10 -m pip install -U git+https://github.com/abetlen/llama-cpp-python.git 
```
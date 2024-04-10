# Các bước để cài đặt chạy TTS
1. Download docker image 
```
docker pull tupkdocker/tts:client
```
2. download checkpoint và để vào thư mục models
```
gdown --id 1xVoVsHQvianSmJFKB6icr95xLNISSSfU
```
3. rename
```
mv name.pth hn_female.pth
```
4. run container
```
docker run -d --rm --gpus all -p 6688:6688 -v path_to_model:/models tupkdocker/tts:client
```

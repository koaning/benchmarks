install:
	python -m pip install --upgrade pip 
	python -m pip install -r requirements.txt

download:
	wget https://raw.githubusercontent.com/koaning/tokenwiser/main/data/oos-intent.jsonl

benchmark:
	rm -rf *.bin
	python -m memray run --output sklearn.bin experiment.py --model sklearn
	python -m memray run --output skearly.bin experiment.py --model skearly
	python -m memray run --output keras.bin experiment.py --model keras
	rm -rf *.html
	python -m memray stats sklearn.bin
	python -m memray stats skearly.bin
	python -m memray stats keras.bin

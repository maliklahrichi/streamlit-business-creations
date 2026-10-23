install:
	pip install -r requirements.txt

data:
	python -m scripts.download_data
	python -m scripts.build_data

test:
	python -m pytest -q

run:
	streamlit run app.py

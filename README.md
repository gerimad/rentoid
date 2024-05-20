# setup:

python3.12
python3 -m venv venv
source venv/bin/activate

pip install requests
pip install flask flask-bootstrap flask-wtf
pip install beautifulsoup4


pip install spacy -U
pip install huspacy -U

pip install -U transformers datasets evaluate rouge_score
pip install -U accelerate
pip install -U tensorflow

pip install Flask-SQLAlchemy

# the plan:

## Major Checkpoints:
- Collecting the data
- Summary Page
- Rating-Reccomendation Page
- Favourites Page
- Packaged Version Deluxxe
- Documentation 

## Tasks:
- Collecting the data
    - scraping all the data from website 
    - 403 prevention 
    - analyze extra unlabeled data to determine most common features to classify
    - store in DB
- Summary Page
    - get the transformer model and load it in wrapper 
    - input text -> summary
    - input text -> classification
        - Train classfication head
- Rating-Reccomendation Page
    - display listing summary and classification from the db
    - allow rating it
        - ? based on fixed criteria
    - implement reccomendation system
    - save to favorites button
- Favourites Page
    - display favourites and stuff
- Packaged Version Deluxxe
    - dependecies
    - single setup script
    - Cosmetic js for swiping
- Documentation
    - read reqs
    - TODO

## Possible Roadblocks
- 
#!/bin/bash

docker build -t bonus:1.0 .

docker run --env-file env.txt -v ${pwd}:/app -it bonus:1.0  python main.py --kaggle_dataname "brkurzawa/us-breweries" --s3_bucket big-data-spark1
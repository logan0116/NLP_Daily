  docker run \
    -it \
    --rm \
    --network=host \
    --name chat_server \
    --gpus all \
    --shm-size 32G \
    -v /home/python_projects/NLP_Daily:/NLP_Daily \
    -w /NLP_Daily/chat_server \
    llm:v1.4 \
    python3 main.py --port 9010
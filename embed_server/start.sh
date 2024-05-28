 docker run \
    -it \
    --rm \
    --name fd_embed \
    --network=host \
    --gpus all \
    --shm-size 32G \
    -v /home/mozinode4p/.cache/huggingface/hub:/root/.cache/huggingface/hub \
    -v /home/mozinode4p/PycharmProjects/NLP_Daily:/NLP_Daily \
    -w /NLP_Daily/embed_server \
    -e TRANSFORMERS_OFFLINE=1 \
    llm:v1.4.1 \
    python3 main.py
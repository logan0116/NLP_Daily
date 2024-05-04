 docker run \
    -it \
    --rm \
    --name fd_embed \
    --network=host \
    --gpus all \
    --shm-size 32G \
	  -v /root/.cache/huggingface/hub:/root/.cache/huggingface/hub \
    -v /home/python_projects/NLP_Daily:/NLP_Daily \
    -w /NLP_Daily/embed_server \
    -e TRANSFORMER_OFFLINE=1 \
    llm:v1.4 \
    python3 main.py
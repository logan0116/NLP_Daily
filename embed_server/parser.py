import argparse


def parameter_parser():
    parser = argparse.ArgumentParser(description='for Chat')
    parser.add_argument('--embed_model_path', help="Please give a embed_model_path",
                        default='BAAI/bge-large-en-v1.5', type=str)

    return parser.parse_args()

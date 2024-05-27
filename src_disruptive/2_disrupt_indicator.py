import json
from tqdm import tqdm


def disrupt_single(node, node2neighbor_left, node2neighbor_right):
    """
    颠覆性指标
    :param node:
    :param node2neighbor_left:
    :param node2neighbor_right:
    :return:
    """

    if len(node2neighbor_left[node]) == 0 or len(node2neighbor_right[node]) == 0:
        return 0

    target_set_1 = node2neighbor_left[node]
    target_set_2 = set()
    for neighbor in node2neighbor_right[node]:
        target_set_2 = target_set_2 | node2neighbor_left[neighbor]

    # ni node in target_set_1 not in target_set_2
    ni = len(target_set_1 - target_set_2)
    # nj node in target_set_2 in target_set_1
    nj = len(target_set_1 & target_set_2)
    # nk node in target_set_2 not in target_set_1
    nk = len(target_set_2 - target_set_1)

    return (ni - nj) / (ni + nj + nk)


def disrupt(node2neighbor_left, node2neighbor_right):
    """
    颠覆性指标
    只基于引用网络来做
    :param node2neighbor_left:
    :param node2neighbor_right:
    :return:
    """
    # node_set 并集
    node_set = list(set(node2neighbor_left.keys()) | set(node2neighbor_right.keys()))
    # disrupt
    node2disrupt = {}
    for node in tqdm(node_set, total=len(node_set)):
        node2disrupt[node] = disrupt_single(node, node2neighbor_left, node2neighbor_right)

    return node2disrupt


def main():
    with open('graph/link/paper_id2neighbor_left.json', 'r') as f:
        node2neighbor_left = json.load(f)
    with open('graph/link/paper_id2neighbor_right.json', 'r') as f:
        node2neighbor_right = json.load(f)

    # link2set
    node2neighbor_left = {k: set(v) for k, v in node2neighbor_left.items()}
    node2neighbor_right = {k: set(v) for k, v in node2neighbor_right.items()}

    node2disrupt = disrupt(node2neighbor_left, node2neighbor_right)

    # save disrupt
    with open('graph/link/paper_id2disrupt.json', 'w') as f:
        json.dump(node2disrupt, f)


if __name__ == '__main__':
    main()

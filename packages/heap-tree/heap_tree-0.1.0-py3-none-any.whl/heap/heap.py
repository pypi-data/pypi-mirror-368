from collections import deque
from .node import Node

class Heap:
    def __init__(self, is_min_heap=False):
        """
        Initialize heap.
        :param is_min_heap: False for max heap (default), True for min heap
        """
        self.root = None
        self.is_min_heap = is_min_heap

    # -------- Utility Compare -------- #
    def _compare(self, a, b):
        return a < b if self.is_min_heap else a > b

    # -------- Insert -------- #
    def insert(self, val):
        if self.root is None:
            self.root = Node(val)
            return

        queue = deque([self.root])
        while queue:
            curr_node = queue.popleft()
            if curr_node.left is None:
                curr_node.left = Node(val)
                self.heapify_up(curr_node.left)
                break
            else:
                queue.append(curr_node.left)

            if curr_node.right is None:
                curr_node.right = Node(val)
                self.heapify_up(curr_node.right)
                break
            else:
                queue.append(curr_node.right)

    # -------- Heapify Up -------- #
    def heapify_up(self, node):
        if node is None or node == self.root:
            return
        parent_node = self.find_parent(self.root, node)
        if parent_node and self._compare(node.val, parent_node.val):
            parent_node.val, node.val = node.val, parent_node.val
            self.heapify_up(parent_node)

    # -------- Find Parent -------- #
    def find_parent(self, root, node):
        if root is None:
            return None
        queue = deque([root])
        while queue:
            curr_node = queue.popleft()
            if curr_node.left == node or curr_node.right == node:
                return curr_node
            if curr_node.left:
                queue.append(curr_node.left)
            if curr_node.right:
                queue.append(curr_node.right)
        return None

    # -------- Find Last Node -------- #
    def find_last_node(self):
        if self.root is None:
            return None
        queue = deque([self.root])
        last_node = None
        while queue:
            last_node = queue.popleft()
            if last_node.left:
                queue.append(last_node.left)
            if last_node.right:
                queue.append(last_node.right)
        return last_node

    # -------- Remove Root -------- #
    def remove(self):
        if self.root is None:
            return None

        last_node = self.find_last_node()

        if last_node == self.root:
            removed_val = self.root.val
            self.root = None
            return removed_val

        parent_node = self.find_parent(self.root, last_node)
        removed_val = self.root.val

        self.root.val = last_node.val

        if parent_node.left == last_node:
            parent_node.left = None
        elif parent_node.right == last_node:
            parent_node.right = None

        self.heapify_down(self.root)
        return removed_val

    # -------- Heapify Down -------- #
    def heapify_down(self, node):
        if node is None:
            return
        target = node
        if node.left and self._compare(node.left.val, target.val):
            target = node.left
        if node.right and self._compare(node.right.val, target.val):
            target = node.right
        if target != node:
            node.val, target.val = target.val, node.val
            self.heapify_down(target)

    # -------- Peek -------- #
    def peek(self):
        return -1 if self.root is None else self.root.val

    # -------- Print Level Order -------- #
    def print(self):
        if self.root is None:
            print("Heap is empty")
            return
        queue = deque([self.root])
        while queue:
            level_size = len(queue)
            level_nodes = []
            for _ in range(level_size):
                curr_node = queue.popleft()
                level_nodes.append(str(curr_node.val))
                if curr_node.left:
                    queue.append(curr_node.left)
                if curr_node.right:
                    queue.append(curr_node.right)
            print(" ".join(level_nodes))

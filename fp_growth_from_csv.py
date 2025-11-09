import pandas as pd
from collections import defaultdict

# -----------------------------
# STEP 1 — LOAD TRANSACTIONS
# -----------------------------
print("📂 Reading dataset...")
df = pd.read_csv("fp_transactions_1000.csv")

# Convert "Items" column into list of items
transactions = [row.split(",") for row in df["Items"].astype(str)]

print(f"✅ Loaded {len(transactions)} transactions from CSV file.\n")

# -----------------------------
# STEP 2 — FP-GROWTH FUNCTIONS
# -----------------------------
class FPNode:
    def __init__(self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None

    def increment(self, count):
        self.count += count

class FPTree:
    def __init__(self):
        self.root = FPNode(None, 1, None)
        self.header_table = defaultdict(list)

    def add_transaction(self, transaction, count=1):
        current_node = self.root
        for item in transaction:
            if item not in current_node.children:
                new_node = FPNode(item, count, current_node)
                current_node.children[item] = new_node
                self.header_table[item].append(new_node)
            else:
                current_node.children[item].increment(count)
            current_node = current_node.children[item]

def find_frequent_items(transactions, min_support):
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    return {item: count for item, count in item_counts.items() if count >= min_support}

def construct_fp_tree(transactions, min_support):
    frequent_items = find_frequent_items(transactions, min_support)
    if not frequent_items:
        return None, None

    sorted_items = sorted(frequent_items.items(), key=lambda x: (-x[1], x[0]))
    tree = FPTree()

    for transaction in transactions:
        sorted_trans = [item for item, _ in sorted_items if item in transaction]
        tree.add_transaction(sorted_trans)

    return tree, sorted_items

def mine_fp_tree(tree, header_table, min_support, prefix, frequent_patterns):
    for item, nodes in header_table.items():
        new_pattern = prefix.copy()
        new_pattern.add(item)
        support = sum(node.count for node in nodes)
        frequent_patterns[frozenset(new_pattern)] = support

        # Build conditional pattern base
        conditional_patterns = []
        for node in nodes:
            path = []
            parent = node.parent
            while parent and parent.item:
                path.append(parent.item)
                parent = parent.parent
            for _ in range(node.count):
                conditional_patterns.append(path)

        # Construct conditional FP-tree
        cond_tree, cond_header = construct_fp_tree(conditional_patterns, min_support)
        if cond_tree:
            mine_fp_tree(cond_tree, cond_tree.header_table, min_support, new_pattern, frequent_patterns)

def fp_growth(transactions, min_support):
    tree, header_table = construct_fp_tree(transactions, min_support)
    frequent_patterns = {}
    if tree:
        mine_fp_tree(tree, tree.header_table, min_support, set(), frequent_patterns)
    return frequent_patterns

# -----------------------------
# STEP 3 — RUN FP-GROWTH
# -----------------------------
min_support = 2  # you can increase if you want fewer patterns

print("⚙️ Running FP-Growth algorithm...")
patterns = fp_growth(transactions, min_support)

# -----------------------------
# STEP 4 — DISPLAY RESULTS
# -----------------------------
print(f"\n✅ Total Frequent Itemsets Found: {len(patterns)}\n")
print("🔹 Showing up to 1000 frequent itemsets:\n")

count = 0
for pattern, support in sorted(patterns.items(), key=lambda x: (-x[1], list(x[0]))):
    print(f"{list(pattern)} : {support}")
    count += 1
    if count >= 1000:
        break

print("\n🎯 FP-Growth mining complete.")

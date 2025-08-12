// dynamic_segment_tree/_dseg.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <memory>
#include <vector>

namespace py = pybind11;

// Node of dynamic segment tree
struct Node {
    Node* left = nullptr;
    Node* right = nullptr;
    int l, r;
    std::unordered_map<int, long long> freq; // category -> count

    Node(int L, int R) : left(nullptr), right(nullptr), l(L), r(R) {}
};

class DynamicSegTree {
public:
    // Construct tree for index range [0, N-1]
    DynamicSegTree(long long N) : N((int)N) {
        root = new Node(0, N - 1);
    }

    ~DynamicSegTree() {
        destroy(root);
    }

    // set position pos to category newCat (if previously had category oldCat, it's replaced)
    // The class stores current categories in pos_map, so caller supplies just pos,newCat.
    void set(long long pos, int newCat) {
        if (pos < 0 || pos >= N) throw std::out_of_range("pos out of range");
        int oldCat = -1;
        auto it = pos_map.find((int)pos);
        if (it != pos_map.end()) oldCat = it->second;
        if (oldCat == newCat) return; // no-op

        update_rec(root, (int)pos, oldCat, newCat);
        pos_map[(int)pos] = newCat;
    }

    // build from vector<int> where arr[i] = category at position i.
    // Implementation: call set() for each touched position to keep allocation sparse.
    void build(const std::vector<int>& arr) {
        for (size_t i = 0; i < arr.size(); ++i) {
            set((long long)i, arr[i]);
        }
    }

    // query how many times 'cat' appears in [ql, qr]
    long long query(long long ql, long long qr, int cat) {
        if (ql < 0) ql = 0;
        if (qr >= N) qr = N - 1;
        if (ql > qr) return 0;
        return query_rec(root, (int)ql, (int)qr, cat);
    }

    // optional helper to get current category at a position; returns -1 if not set
    int get(long long pos) const {
        auto it = pos_map.find((int)pos);
        if (it == pos_map.end()) return -1;
        return it->second;
    }

private:
    Node* root;
    int N;
    std::unordered_map<int,int> pos_map;

    void destroy(Node* node) {
        if (!node) return;
        destroy(node->left);
        destroy(node->right);
        delete node;
    }

    // update node counts along path to pos: decrement oldCat (if != -1), increment newCat (if != -1)
    void update_rec(Node* node, int pos, int oldCat, int newCat) {
        // update this node's freq map
        if (oldCat != -1) {
            auto it = node->freq.find(oldCat);
            if (it != node->freq.end()) {
                it->second -= 1;
                if (it->second == 0) node->freq.erase(it);
            }
        }
        if (newCat != -1) {
            node->freq[newCat] += 1;
        }

        if (node->l == node->r) {
            // leaf done
            return;
        }

        int mid = (node->l + node->r) >> 1;
        if (pos <= mid) {
            if (!node->left) node->left = new Node(node->l, mid);
            update_rec(node->left, pos, oldCat, newCat);
        } else {
            if (!node->right) node->right = new Node(mid + 1, node->r);
            update_rec(node->right, pos, oldCat, newCat);
        }
    }

    long long query_rec(Node* node, int ql, int qr, int cat) const {
        if (!node) return 0;
        if (qr < node->l || ql > node->r) return 0;
        if (ql <= node->l && node->r <= qr) {
            auto it = node->freq.find(cat);
            if (it == node->freq.end()) return 0;
            return it->second;
        }
        long long res = 0;
        if (node->left) res += query_rec(node->left, ql, qr, cat);
        if (node->right) res += query_rec(node->right, ql, qr, cat);
        return res;
    }
};

// Pybind11 module
PYBIND11_MODULE(_dseg, m) {
    py::class_<DynamicSegTree>(m, "DynamicSegTree")
        .def(py::init<long long>(), py::arg("N"))
        .def("set", &DynamicSegTree::set, py::arg("pos"), py::arg("new_cat"))
        .def("build", &DynamicSegTree::build, py::arg("arr"))
        .def("query", &DynamicSegTree::query, py::arg("ql"), py::arg("qr"), py::arg("cat"))
        .def("get", &DynamicSegTree::get, py::arg("pos"));
}

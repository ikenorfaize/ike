from flask import Flask, render_template, request
import heapq

app = Flask(__name__)

class LaundryGraph:
    def __init__(self):
        self.graph = {}
        self.pembayaran_options = ["transfer", "cash"]
        self.layanan_options = ["cuci kering", "cuci basah", "cuci setrika"]

    def get_name_options(self):
        return list(self.graph.keys())
    def get_pembayaran_options(self):
        return self.pembayaran_options

    def get_layanan_options(self):
        return self.layanan_options

    def get_anjem_options(self):
        return self.anjem_options
    
    def add_laundry(self, laundry_id, lokasi, pembayaran_options, layanan_options, anjem):
        self.graph[laundry_id] = {"lokasi": lokasi, "pembayaran_options": pembayaran_options, "layanan_options": layanan_options,
            "anjem": anjem
        }

    def add_edge(self, laundry1, laundry2):
        distance = self.calculate_distance(self.graph[laundry1]["lokasi"], self.graph[laundry2]["lokasi"])
        self.graph[laundry1].setdefault("edges", []).append((laundry2, distance))
        self.graph[laundry2].setdefault("edges", []).append((laundry1, distance))

    def calculate_distance(self, lokasi1, lokasi2):
        return ((lokasi1[0] - lokasi2[0])*2 + (lokasi1[1] - lokasi2[1])*2)*0.5

    def heuristic(self, node, goal):
        # A simple Euclidean distance heuristic
        return self.calculate_distance(self.graph[node]["lokasi"], self.graph[goal]["lokasi"])

    def find_nearest_laundry(self, start, pembayaran_option=None, layanan_option=None, anjem=None):
        priority_queue = [(0, start)]
        visited = set()

        while priority_queue:
            (current_cost, current_node) = heapq.heappop(priority_queue)

            if current_node not in visited:
                visited.add(current_node)

                if (
                    pembayaran_option is None or pembayaran_option in self.graph[current_node]["pembayaran_options"]
                ) and (
                    layanan_option is None or layanan_option in self.graph[current_node]["layanan_options"]
                ) and (
                    anjem is False or anjem == self.graph[current_node]["anjem"]
                ):
                    return current_node

                for (neighbor, distance) in self.graph[current_node].get("edges", []):
                    if neighbor not in visited:
                        heuristic_cost = self.heuristic(neighbor, start)
                        heapq.heappush(priority_queue, (current_cost + distance + heuristic_cost, neighbor))

        return None  # No suitable laundry found


laundry_app = LaundryGraph()

# Menambahkan data laundry
laundry_app.add_laundry("laundryA", (0, 0), ["transfer", "cash"], ["cuci kering", "cuci basah"], True)
laundry_app.add_laundry("laundryB", (2, 3), ["cash"], ["cuci kering", "cuci basah", "cuci setrika"], False)
laundry_app.add_laundry("laundryC", (5, 4), ["transfer", "cash"], ["cuci kering", "cuci basah", "cuci setrika"], True)
laundry_app.add_laundry("laundryD", (6, 4), ["transfer"], ["cuci kering", "cuci basah", "cuci setrika"], False)
laundry_app.add_laundry("laundryE", (7, 3), ["transfer", "cash"], ["cuci kering", "cuci basah", "cuci setrika"], True)
laundry_app.add_laundry("laundryF", (4, 3), ["transfer", "cash"], ["cuci setrika"], False)
laundry_app.add_laundry("laundryG", (3, 6), ["transfer", "cash"], ["cuci kering", "cuci basah"], False)
laundry_app.add_laundry("laundryH", (6, 5), ["transfer"], ["cuci kering", "cuci basah", "cuci setrika"], True)
laundry_app.add_laundry("laundryI", (7, 6), ["transfer", "cash"], ["cuci kering", "cuci basah", "cuci setrika"], False)
laundry_app.add_laundry("laundryJ", (3, 7), ["transfer", "cash"], ["cuci kering", "cuci basah", "cuci setrika"], False)

# Menambahkan koneksi antar laundry
laundry_app.add_edge("laundryA", "laundryB")
laundry_app.add_edge("laundryB", "laundryC")
laundry_app.add_edge("laundryA", "laundryC")
laundry_app.add_edge("laundryC", "laundryD")
laundry_app.add_edge("laundryD", "laundryF")
laundry_app.add_edge("laundryB", "laundryE")
laundry_app.add_edge("laundryE", "laundryF")
laundry_app.add_edge("laundryE", "laundryJ")
laundry_app.add_edge("laundryD", "laundryH")
laundry_app.add_edge("laundryH", "laundryI")

@app.route('/')
def index():
    return render_template('index.html', nama_laundry_options=laundry_app.get_name_options(),
                           pembayaran_options=laundry_app.get_pembayaran_options(),
                                        layanan_options=laundry_app.get_layanan_options())

@app.route('/find_nearest_laundry', methods=['POST'])
def find_nearest_laundry():
    nama_laundry = request.form['nama_laundry']
    pembayaran_option = request.form['pembayaran_option']
    layanan_option = request.form['layanan_option']
    anjem_input = request.form['anjem_input']
    
    if anjem_input == "TRUE":
        anjem_input = True
    else:
        anjem_input = False

    nearest_laundry = laundry_app.find_nearest_laundry(nama_laundry, pembayaran_option=pembayaran_option, layanan_option=layanan_option, anjem=anjem_input)
    if nearest_laundry:
        if nearest_laundry == nama_laundry:
            result = f"Laundry {nearest_laundry} memenuhi kriteria laundry yang kamu cari"
        else:
            result = f"{nama_laundry} belum memenuhi kriteria. Coba laundry terdekat dari {nama_laundry} yaitu {nearest_laundry}"
    else:
        result = "Tidak ada laundry yang ditemukan."

    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Implement logic untuk autentikasi (contoh sederhana)
    if username == 'user' and password == 'password':
        return redirect(url_for('success'))
    else:
        return render_template('login.html', message='Login failed. Please try again.')

@app.route('/success')
def success():
    return 'Login successful!'
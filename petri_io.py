from pathlib import Path
import xml.etree.ElementTree as ET

class Parser:

    def __init__(self):
        self.places = []
        self.trans = []
        self.edges = []
        self.mark = {}
        self.root = None

    def validate(self):
        # 1. Duplikate prüfen
        place_ids = [p['id'] for p in self.places]
        trans_ids = [t['id'] for t in self.trans]

        if len(place_ids) != len(set(place_ids)):
            raise ValueError("Duplikate bei Place-IDs gefunden.")
        if len(trans_ids) != len(set(trans_ids)):
            raise ValueError("Duplikate bei Transition-IDs gefunden.")

        # 2. Arc-Quellen/Ziele prüfen
        valid_ids = set(place_ids) | set(trans_ids)
        for arc in self.edges:
            src = arc['src']
            dst = arc['dst']
            if src not in valid_ids:
                raise ValueError(f"Arc-Quelle '{src}' existiert nicht.")
            if dst not in valid_ids:
                raise ValueError(f"Arc-Ziel '{dst}' existiert nicht.")

            # 3. Prüfen Richtung der Kante
            if (src in place_ids and dst in place_ids) or (src in trans_ids and dst in trans_ids):
                raise ValueError(
                    f"Ungültige Kante: {src} → {dst}. Kanten dürfen nur Place → Transition oder Transition → Place sein.")

        # 4. Initial Marking prüfen
        for pid, tokens in self.mark.items():
            if pid not in place_ids:
                raise ValueError(f"Initial Marking referenziert unbekannte Place-ID '{pid}'.")
            elif tokens < 0:
                raise ValueError(f"Initial Marking ungültig '{tokens}'.")

        print("Parser-Validierung erfolgreich.")
        return True

    def parse(self, file):
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"Datei existiert nicht: {file}")

        if not path.is_file():
            raise ValueError(f"Kein gültiger Dateipfad: {file}")

        try:
            tree = ET.parse(path)
            self.root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Ungültiges XML: {e}")
        except Exception as e:
            raise IOError(f"Datei konnte nicht gelesen werden: {e}")

        self.parse_places()
        self.parse_trans()
        self.parse_edges()
        self.parse_initial_marking()
        self.validate()

        return self.get_controller_data()


    def get_controller_data(self):
        place_ids = [p["id"] for p in self.places]
        place_index = {pid: i for i, pid in enumerate(place_ids)}

        # Places-Tupel
        places_tup = []
        for p in self.places:
            pid, name, x, y = p["id"], p["name"], p["x"], p["y"]
            val = self.mark.get(pid, 0)
            places_tup.append((pid, name, x, y, val))

        transitions_tup = []
        num_places = len(self.places)

        for t in self.trans:
            tid, name, x, y = t["id"], t["name"], t["x"], t["y"]
            pre = [0] * num_places
            post = [0] * num_places

            for arc in self.edges:
                src, dst, w = arc["src"], arc["dst"], arc["weight"]
                if dst == tid and src in place_index:
                    pre[place_index[src]] = w
                if src == tid and dst in place_index:
                    post[place_index[dst]] = w

            transitions_tup.append((tid, name, x, y, tuple(pre), tuple(post)))

        return places_tup, transitions_tup


    def parse_places(self):
        for p in self.root.findall(".//place"):
            pid = p.get("id")
            name_elem = p.find(".//name//text")
            name = name_elem.text.strip() if name_elem is not None else pid

            pos_elem = p.find(".//graphics//position")
            x = float(pos_elem.get("x", 0)) if pos_elem is not None else 0
            y = float(pos_elem.get("y", 0)) if pos_elem is not None else 0

            self.places.append({"id": pid, "name": name, "x": x, "y": y})

    def parse_trans(self):
        for t in self.root.findall(".//transition"):
            tid = t.get("id")
            name_elem = t.find(".//name//text")
            name = name_elem.text.strip() if name_elem is not None else tid

            pos_elem = t.find(".//graphics//position")
            x = float(pos_elem.get("x", 0)) if pos_elem is not None else 0
            y = float(pos_elem.get("y", 0)) if pos_elem is not None else 0

            self.trans.append({"id": tid, "name": name, "x": x, "y": y})

    def parse_edges(self):
        for a in self.root.findall(".//arc"):
            src = a.get("source")
            dst = a.get("target")
            inscription_elem = a.find(".//inscription//text")
            try:
                weight = int(inscription_elem.text.strip())
            except:
                weight = 1
            self.edges.append({"src": src, "dst": dst, "weight": weight})

    def parse_initial_marking(self):
        for p in self.root.findall(".//place"):
            pid = p.get("id")
            im = p.find(".//initialMarking//text")
            if im is not None:
                try:
                    m = int(im.text.strip())
                except:
                    m = 0
                self.mark[pid] = m
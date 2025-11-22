from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Any

class Parser:
    """
    A class for parsing PNML (Petri Net Markup Language) files.
    """

    def __init__(self) -> None:
        """
        Initialize the Parser.
        """
        self.places: list[dict[str, Any]] = []
        self.trans: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.mark: dict[str, int] = {}
        self.root: ET.Element | None = None

    def validate(self) -> bool:
        """
        Validate the parsed Petri net data.

        Returns:
            True if the data is valid.

        Raises:
            ValueError: If duplicates, invalid arcs, or invalid markings are found.
        """
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

    def parse(self, file: str) -> tuple[list[tuple[str, str, float, float, int]], list[tuple[str, str, float, float, tuple[int, ...], tuple[int, ...]]]]:
        """
        Parse a PNML file.

        Args:
            file: The path to the PNML file.

        Returns:
            A tuple containing the places and transitions data for the controller.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file path is invalid or the XML is invalid.
            IOError: If the file cannot be read.
        """
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


    def get_controller_data(self) -> tuple[list[tuple[str, str, float, float, int]], list[tuple[str, str, float, float, tuple[int, ...], tuple[int, ...]]]]:
        """
        Format the parsed data for the controller.

        Returns:
            A tuple containing lists of places and transitions.
        """
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


    def parse_places(self) -> None:
        """
        Parse places from the XML root.
        """
        if self.root is None:
            return
        for p in self.root.findall(".//place"):
            pid = p.get("id")
            name_elem = p.find(".//name//text")
            name = name_elem.text.strip() if name_elem is not None and name_elem.text else pid

            pos_elem = p.find(".//graphics//position")
            x = float(pos_elem.get("x", 0)) if pos_elem is not None else 0.0
            y = float(pos_elem.get("y", 0)) if pos_elem is not None else 0.0

            self.places.append({"id": pid, "name": name, "x": x, "y": y})

    def parse_trans(self) -> None:
        """
        Parse transitions from the XML root.
        """
        if self.root is None:
            return
        for t in self.root.findall(".//transition"):
            tid = t.get("id")
            name_elem = t.find(".//name//text")
            name = name_elem.text.strip() if name_elem is not None and name_elem.text else tid

            pos_elem = t.find(".//graphics//position")
            x = float(pos_elem.get("x", 0)) if pos_elem is not None else 0.0
            y = float(pos_elem.get("y", 0)) if pos_elem is not None else 0.0

            self.trans.append({"id": tid, "name": name, "x": x, "y": y})

    def parse_edges(self) -> None:
        """
        Parse arcs (edges) from the XML root.
        """
        if self.root is None:
            return
        for a in self.root.findall(".//arc"):
            src = a.get("source")
            dst = a.get("target")
            inscription_elem = a.find(".//inscription//text")
            try:
                weight = int(inscription_elem.text.strip()) if inscription_elem is not None and inscription_elem.text else 1
            except:
                weight = 1
            self.edges.append({"src": src, "dst": dst, "weight": weight})

    def parse_initial_marking(self) -> None:
        """
        Parse initial markings from the XML root.
        """
        if self.root is None:
            return
        for p in self.root.findall(".//place"):
            pid = p.get("id")
            im = p.find(".//initialMarking//text")
            if im is not None and im.text:
                try:
                    m = int(im.text.strip())
                except:
                    m = 0
                if pid:
                    self.mark[pid] = m
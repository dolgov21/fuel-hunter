import http.client
import json
import random
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OSM_IDS_FILE = BASE_DIR / "osm_ids"
OUTPUT_FILE = BASE_DIR / "comments.json"
HOST = "gdebenz.ru"
REQUEST_DELAY_MIN = 0.2
REQUEST_DELAY_MAX = 0.7


def load_osm_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def fetch_comments(conn: http.client.HTTPSConnection, osm_id: str):
    conn.request("GET", f"/api/comments/{osm_id}")
    response = conn.getresponse()
    body = response.read().decode("utf-8")

    if response.status != 200:
        return {
            "osm_id": osm_id,
            "status": response.status,
            "error": body,
        }

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {
            "osm_id": osm_id,
            "status": response.status,
            "raw": body,
        }


def main():
    osm_ids = load_osm_ids(OSM_IDS_FILE)
    conn = http.client.HTTPSConnection(HOST, timeout=30)

    try:
        with OUTPUT_FILE.open("w", encoding="utf-8") as output_file:
            output_file.write("[\n")

            for index, osm_id in enumerate(osm_ids, start=1):
                print(f"[{index}/{len(osm_ids)}] {osm_id}")
                result = fetch_comments(conn, osm_id)

                if index > 1:
                    output_file.write(",\n")

                output_file.write(json.dumps(result, ensure_ascii=False, indent=2))
                output_file.flush()

                if index < len(osm_ids):
                    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

            output_file.write("\n]\n")
            output_file.flush()
    finally:
        conn.close()

    print(f"Saved {len(osm_ids)} responses to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

import urllib.request
import urllib.error
import os

papers = {
    "hep-th_9602022": "https://arxiv.org/pdf/hep-th/9602022.pdf",
    "hep-th_9602114": "https://arxiv.org/pdf/hep-th/9602114.pdf",
    "1806.01854": "https://arxiv.org/pdf/1806.01854.pdf"
}

output_dir = "references"
os.makedirs(output_dir, exist_ok=True)

for name, url in papers.items():
    output_path = os.path.join(output_dir, f"{name}.pdf")
    print(f"Fetching {name} from {url}...")
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"Successfully downloaded {name}.pdf")
    except urllib.error.HTTPError as e:
        print(f"Failed to download {name}: HTTP Error {e.code}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")

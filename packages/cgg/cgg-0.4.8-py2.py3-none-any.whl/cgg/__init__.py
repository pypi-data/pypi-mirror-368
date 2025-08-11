# !/usr/bin/env python3

__version__="0.4.8"

import argparse, json, random, os.path, urllib.request, subprocess
from rich.progress import Progress

def get_file_size(url):
    with urllib.request.urlopen(url) as response:
        size = int(response.headers['Content-Length'])
    return size
def format_size(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB"
def clone_file(url):
    try:
        file_size = get_file_size(url)
        filename = os.path.basename(url)
        with Progress(transient=True) as progress:
            task = progress.add_task(f"Downloading {filename}", total=file_size)
            with urllib.request.urlopen(url) as response, open(filename, 'wb') as file:
                chunk_size = 1024
                downloaded = 0
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded += len(chunk)
                    progress.update(task, completed=downloaded, description=f"Downloading {filename} [green][{format_size(downloaded)} / {format_size(file_size)}]")
        print(f"File cloned successfully and saved as '{filename}'({format_size(file_size)}) in the current directory.")
    except Exception as e:
        print(f"Error: {e}")
def read_json_file(file_path):
    response = urllib.request.urlopen(file_path)
    data = json.loads(response.read())
    # with open(file_path, 'r') as file:
        # data = json.load(file)
    return data
def extract_names(data):
    for idx, entry in enumerate(data, start=1):
        print(f'{idx}. {entry["name"]}')
def handle_user_input(data):
    while True:
        user_choice = input(f"Enter your choice (1 to {len(data)}) or 'q' to quit: ")
        if user_choice.lower() == 'q':
            break
        try:
            index = int(user_choice)
            if 1 <= index <= len(data):
                source_url = data[index - 1]["url"]
                clone_file(source_url)
                break
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
# def generate_descriptor(descriptors):
#     descriptor = []
#     for key, values in descriptors.items():
#         choice = random.choice(values)
#         descriptor.append(f"{key.replace('_', ' ')}: {choice}")
#     return ", ".join(descriptor)
def generate_descriptor_fixed(descriptors):
    """Generate a single random descriptor in a readable format."""
    subject = random.choice(descriptors.get("subject", []))
    hair_color = random.choice(descriptors.get("hair_color", []))
    eye_color = random.choice(descriptors.get("eye_color", []))
    scene = random.choice(descriptors.get("scene", []))
    return f"A {hair_color} haired {subject} with {eye_color} eyes, {scene}."
def clone_github_repo(repo_url):
    try:
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        if os.path.exists(repo_name):
            print(f"Error: A folder named '{repo_name}' already exists in the current directory.")
            return
        print(f"Cloning repository '{repo_url}'...")
        subprocess.run(["git", "clone", repo_url], check=True)
        print(f"Repository '{repo_name}' cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to clone the repository. {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
def __init__():
    parser = argparse.ArgumentParser(description="cgg will execute different functions based on command-line arguments")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    # Subparser session below
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    # Subparser for 'clone [URL]' subcommand
    clone_parser = subparsers.add_parser('clone', help='download a GGUF file/model from URL')
    clone_parser.add_argument('url', type=str, help='URL to download from (i.e., cgg clone [url])')
    # Subparser for 'menu/cpp/c/gpp/g/s/r/us...etc.' subcommand
    subparsers.add_parser('menu', help='connector selection list:')
    subparsers.add_parser('cpp', help='cpp connector')
    subparsers.add_parser('gpp', help='gpp connector')
    subparsers.add_parser('c', help='c connector')
    subparsers.add_parser('g', help='g connector')
    subparsers.add_parser('v', help='v connector')
    subparsers.add_parser('r', help='metadata reader')
    subparsers.add_parser('a', help='model analyzor')
    subparsers.add_parser('d', help='model divider')
    subparsers.add_parser('m', help='model merger')
    subparsers.add_parser('n', help='clone GGUF node   (internet required)')
    subparsers.add_parser('y', help='clone GGUF comfy  (internet required)')
    subparsers.add_parser('p', help='clone GGUF pack   (internet required)')
    subparsers.add_parser('s', help='sample GGUF list  (internet required)')
    subparsers.add_parser('pg', help='prompt generator (internet required)')
    subparsers.add_parser('pc', help='pdf analyzor c')
    subparsers.add_parser('pp', help='pdf analyzor p')
    subparsers.add_parser('oc', help='wav recognizor c (internet required)')
    subparsers.add_parser('op', help='wav recognizor p (internet required)')
    subparsers.add_parser('vc', help='wav recognizor c')
    subparsers.add_parser('vp', help='wav recognizor p')
    subparsers.add_parser('t2i', help='text-to-image generator')
    subparsers.add_parser('t2v', help='text-to-video generator')
    subparsers.add_parser('i2v', help='image-to-video generator')
    subparsers.add_parser('flux', help='connector flux')
    subparsers.add_parser('qwen', help='connector qwen')
    subparsers.add_parser('wan', help='connector wan')
    subparsers.add_parser('ltxv', help='connector ltxv')
    subparsers.add_parser('mochi', help='connector mochi')
    subparsers.add_parser('gudio', help='connector gudio')
    subparsers.add_parser('io', help='launch to gguf.io (mirror of us)')
    subparsers.add_parser('us', help='launch to gguf.us')
    subparsers.add_parser('org', help='launch to gguf.org (same as us)')
    args = parser.parse_args()
    if args.subcommand == 'clone':
        clone_file(args.url)
    elif args.subcommand == 'n':
        repo_url = "https://github.com/calcuis/gguf"
        clone_github_repo(repo_url)
    elif args.subcommand == 'p':
        version = "https://raw.githubusercontent.com/calcuis/gguf-pack/main/version.json"
        ver = read_json_file(version)
        url = f"https://github.com/calcuis/gguf-pack/releases/download/{ver[0]['version']}/GGUF_windows_portable.7z"
        clone_file(url)
    elif args.subcommand == 'y':
        # # version = "https://raw.githubusercontent.com/calcuis/gguf-comfy/main/version.json"
        # version = "https://raw.githubusercontent.com/calcuis/gguf/main/version.json"
        # jdata = read_json_file(version)
        # url = f"https://github.com/calcuis/gguf/releases/download/{jdata[0]['version']}/ComfyUI_GGUF_windows_portable.7z"
        # # url = f"https://github.com/calcuis/gguf-comfy/releases/download/{jdata[0]['version']}/ComfyUI_GGUF_windows_portable.7z"
        # clone_file(url)
        from gguf_connector import y
    elif args.subcommand == 's':
        file_path = "https://raw.githubusercontent.com/calcuis/gguf-connector/main/src/gguf_connector/data.json"
        # file_path = os.path.join(os.path.dirname(__file__), 'data.json')
        json_data = read_json_file(file_path)
        print("Please select a GGUF file to download:")
        extract_names(json_data)
        handle_user_input(json_data)
    elif args.subcommand == 'pg':
        file_path = "https://raw.githubusercontent.com/calcuis/rjj/main/descriptor.json"
        descriptors = read_json_file(file_path)
        if not descriptors:
            return
        try:
            num_descriptors = int(input("Enter the number of descriptors to generate: "))
            if num_descriptors <= 0:
                print("Please enter a positive number.")
                return
            for j in range(1, num_descriptors + 1):
                # descriptor = generate_descriptor(descriptors)
                descriptor = generate_descriptor_fixed(descriptors)
                filename = f"{j}.txt"
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(descriptor)
            print(f"{num_descriptors} prompt(s) generated and saved in separate text file(s).")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    elif args.subcommand == 'org':
        from gguf_connector import o
    elif args.subcommand == 'us':
        from gguf_connector import w
    elif args.subcommand == 'io':
        from gguf_connector import i
    elif args.subcommand == 'r':
        from gguf_connector import r
    elif args.subcommand == 'a':
        from gguf_connector import r2
    elif args.subcommand == 'd':
        from gguf_connector import d2
    elif args.subcommand == 'm':
        from gguf_connector import m2
    elif args.subcommand == 'oc':
        from gguf_connector import cg
    elif args.subcommand == 'op':
        from gguf_connector import pg
    elif args.subcommand == 'vc':
        from gguf_connector import cs
    elif args.subcommand == 'vp':
        from gguf_connector import ps
    elif args.subcommand == 'pc':
        from gguf_connector import cp
    elif args.subcommand == 'pp':
        from gguf_connector import pp
    elif args.subcommand == 'menu':
        from gguf_connector import menu
    elif args.subcommand == 'cpp':
        from gguf_connector import cpp
    elif args.subcommand == 'c':
        from gguf_connector import c
    elif args.subcommand == 'gpp':
        from gguf_connector import gpp
    elif args.subcommand == 'g':
        from gguf_connector import g
    elif args.subcommand == 'v':
        from gguf_connector import v
    elif args.subcommand == 't2i':
        from gguf_connector import i2
    elif args.subcommand == 't2v':
        from gguf_connector import v2
    elif args.subcommand == 'i2v':
        from gguf_connector import vg2
    elif args.subcommand == 'flux':
        from gguf_connector import k
    elif args.subcommand == 'qwen':
        from gguf_connector import q5
    elif args.subcommand == 'wan':
        from gguf_connector import w2
    elif args.subcommand == 'ltxv':
        from gguf_connector import x2
    elif args.subcommand == 'mochi':
        from gguf_connector import m1
    elif args.subcommand == 'gudio':
        from gguf_connector import g2
import ijson
import json

from django.http import StreamingHttpResponse
from django.shortcuts import render
from .forms import JSONDataForm


def upload_json(request):
    if request.method == "POST":
        form = JSONDataForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = form.cleaned_data["json_file"]
            file_name = json_file.name
            try:
                json_data = json.load(json_file)
                formatted_json = json.dumps(json_data, indent=2)
                return render(
                    request,
                    "jsonviewer/display_json_tree.html",
                    {"formatted_json": formatted_json, "file_name": file_name},
                )
            except json.JSONDecodeError:
                return render(
                    request,
                    "jsonviewer/error.html",
                    {"message": "Arquivo JSON inválido"},
                )
    else:
        form = JSONDataForm()
    return render(request, "jsonviewer/base.html", {"form": form})


def process_chunk(chunk, user_to_repos):
    data = json.loads(chunk)
    for record in data:
        user = record["actor"]["login"]
        repo = record["repo"]["name"]
        if user not in user_to_repos:
            user_to_repos[user] = set()
        user_to_repos[user].add(repo)


def generate_json_data(file):
    buffer_size = 1024 * 1024  # 1MB
    while True:
        chunk = file.read(buffer_size)
        if not chunk:
            break
        yield chunk


def display_json_tree(request):
    if request.method == "POST" and "json_file" in request.FILES:
        uploaded_file = request.FILES["json_file"]
        user_to_repos = {}

        # Use ijson to parse JSON incrementally and yield chunks
        parser = ijson.parse(uploaded_file)
        buffer = []
        for prefix, event, value in parser:
            if event == 'start_map':
                buffer.append('{')
            elif event == 'end_map':
                buffer.append('}')
                process_chunk(''.join(buffer), user_to_repos)
                buffer.clear()
            elif event == 'map_key':
                buffer.append(f'"{value}":')
            elif event == 'number' or event == 'string':
                buffer.append(f'"{value}",')

        # Return the result in a JSON format
        result = '{{"user_to_repos": {}}}'.format(json.dumps(user_to_repos))

        return StreamingHttpResponse([result], content_type="application/json")
    else:
        return render(request, "jsonviewer/display_json_tree.html", {"json_data": None})

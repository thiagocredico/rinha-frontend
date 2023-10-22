import ijson
from django.shortcuts import render
from .forms import JSONDataForm
import json


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


def display_json_tree(request):
    if request.method == "POST" and "json_file" in request.FILES:
        uploaded_file = request.FILES["json_file"]

        try:
            json_data = []

            # Create an ijson parser
            parser = ijson.parse(uploaded_file)

            for prefix, event, value in parser:
                if event == "map_key":
                    current_key = value
                elif (
                    event == "number"
                    or event == "string"
                    or event == "boolean"
                    or event == "null"
                ):
                    json_data.append((prefix, current_key, value))

        except ijson.JSONError:
            return render(
                request, "jsonviewer/error.html", {
                    "message": "Arquivo JSON inválido"}
            )

        return render(
            request, "jsonviewer/display_json_tree.html", {
                "json_data": json_data}
        )
    else:
        return render(request, "jsonviewer/display_json_tree.html", {
            "json_data": None})

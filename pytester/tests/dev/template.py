# !/usr/bin/env python
# -*-coding: utf-8 -*-


from jinja2 import Environment, FileSystemLoader


def generate_template(source_folder, source_file, dst_path, key_words):
    env = Environment(loader=FileSystemLoader(searchpath=source_folder))
    template = env.get_template(source_file)
    output = template.render(**key_words)
    with open(dst_path, "w") as fh:
        fh.write(output)

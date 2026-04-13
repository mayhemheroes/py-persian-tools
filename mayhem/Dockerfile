FROM python:3.11-bookworm
RUN apt-get update && apt-get install -y clang
RUN pip3 install atheris

COPY . /py-persian-tools
WORKDIR /py-persian-tools
RUN python3 -m pip install . && chmod +x fuzz/persian_tools_fuzz.py

ENTRYPOINT [ ]
CMD ["/py-persian-tools/fuzz/persian_tools_fuzz.py"]

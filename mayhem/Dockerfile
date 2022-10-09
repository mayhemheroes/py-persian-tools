FROM python:3.8-bullseye
RUN pip3 install atheris

COPY . /py-persian-tools
WORKDIR /py-persian-tools
RUN python3 -m pip install . && chmod +x fuzz/persian_tools_fuzz.py

ENTRYPOINT [ ]
CMD ["/py-persian-tools/fuzz/persian_tools_fuzz.py"]
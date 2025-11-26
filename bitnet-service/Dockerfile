FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    clang \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --recursive --depth 1 https://github.com/microsoft/BitNet.git && rm -rf BitNet/.git

WORKDIR /BitNet

RUN pip install --no-cache-dir -r requirements.txt

RUN python3 utils/codegen_tl2.py --model Llama3-8B-1.58-100B-tokens --BM 256,128,256,128 --BK 96,96,96,96 --bm 32,32,32,32

# Detect architecture and build accordingly
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then \
        cmake -B build -DBITNET_X86_TL2=ON -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++; \
    else \
        cmake -B build -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++; \
    fi

RUN cmake --build build --target llama-server --config Release

EXPOSE 8080

CMD ["python3", "run_inference_server.py", "-m", "model/ggml-model-i2_s.gguf", "--host", "0.0.0.0", "-p", "You are a helpful assistant. Always follow the user's instructions."]

from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import subprocess

router = APIRouter()
DOCKER_IMG_DIR = "docker_images"
os.makedirs(DOCKER_IMG_DIR, exist_ok=True)

def run_cmd(cmd: list[str]):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr.decode())
    return result.stdout.decode()

@router.post("/api/images/upload")
def upload_image(file: UploadFile = File(...)):
    path = os.path.join(DOCKER_IMG_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return {"msg": "镜像文件已保存，待加载", "filename": file.filename}

@router.post("/api/images/load")
def load_image(filename: str):
    path = os.path.join(DOCKER_IMG_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="镜像文件不存在")
    return {"output": run_cmd(["docker", "load", "-i", path])}

@router.post("/api/images/pull")
def pull_image(name: str, tag: str = "latest"):
    return {"output": run_cmd(["docker", "pull", f"{name}:{tag}"])}

@router.get("/api/images/list")
def list_images():
    return {"output": run_cmd(["docker", "images"])}

@router.post("/api/images/tag")
def tag_image(src: str, dst: str):
    return {"output": run_cmd(["docker", "tag", src, dst])}

@router.post("/api/images/push")
def push_image(name: str, tag: str = "latest"):
    return {"output": run_cmd(["docker", "push", f"{name}:{tag}"])}

@router.delete("/api/images/delete")
def delete_image(name: str, tag: str = "latest"):
    return {"output": run_cmd(["docker", "rmi", f"{name}:{tag}"])}

@router.get("/api/images/search")
def search_images(query: str):
    output = run_cmd(["docker", "images"])
    lines = output.splitlines()
    matched = [line for line in lines if query in line]
    return {"matches": matched}
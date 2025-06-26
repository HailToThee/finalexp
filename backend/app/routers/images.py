# routers/images.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import docker

router = APIRouter()
client = docker.from_env()

@router.post("/api/images/upload")
def upload_image(file: UploadFile = File(...)):
    with open(f"docker_images/{file.filename}", "wb") as f:
        f.write(file.file.read())
    return {"msg": "镜像已保存，待上传 Harbor"}

@router.get("/search")
def search_images(query: str):
    # 这里只做本地镜像名模糊搜索
    images = client.images.list()
    result = []
    for img in images:
        for tag in img.tags:
            if query in tag:
                result.append(tag)
    return {"images": result}

@router.post("/pull")
def pull_image(name: str, tag: str):
    try:
        client.images.pull(name, tag=tag)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list")
def list_images():
    images = client.images.list()
    result = []
    for img in images:
        for tag in img.tags:
            name, tag = tag.split(":") if ":" in tag else (tag, "latest")
            result.append({"name": name, "tag": tag})
    return {"images": result}

@router.post("/tag")
def tag_image(name: str, new_tag: str):
    try:
        image = client.images.get(name)
        image.tag(new_tag)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/push")
def push_image(name: str, tag: str):
    try:
        client.images.push(name, tag=tag)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete")
def delete_image(name: str, tag: str):
    try:
        client.images.remove(f"{name}:{tag}")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
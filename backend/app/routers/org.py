from fastapi import APIRouter, HTTPException
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException

router = APIRouter()

def load_kube():
    try:
        config.load_kube_config()
    except ConfigException:
        try:
            config.load_incluster_config()
        except ConfigException:
            raise RuntimeError("无法加载 Kubernetes 配置，请检查集群或 kubeconfig 文件")

@router.post("/api/org/create")
def create_namespace(org_name: str):
    load_kube()
    v1 = client.CoreV1Api()
    namespace = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=org_name)
    )
    try:
        v1.create_namespace(namespace)
        return {"status": "success", "message": f"命名空间 {org_name} 已创建"}
    except client.rest.ApiException as e:
        raise HTTPException(status_code=400, detail=e.body)

@router.post("/api/org/quota")
def set_quota(org_name: str, cpu: str, memory: str, gpu: str = "0"):
    load_kube()
    v1 = client.CoreV1Api()
    quota = client.V1ResourceQuota(
        metadata=client.V1ObjectMeta(name="org-quota", namespace=org_name),
        spec=client.V1ResourceQuotaSpec(
            hard={
                "limits.cpu": cpu,
                "limits.memory": memory,
                "limits.nvidia.com/gpu": gpu
            }
        )
    )
    try:
        v1.create_namespaced_resource_quota(namespace=org_name, body=quota)
        return {"status": "success", "message": "资源配额已设置"}
    except client.rest.ApiException as e:
        raise HTTPException(status_code=400, detail=e.body)

@router.post("/api/org/rbac")
def bind_rbac(org_name: str, user: str, role: str):
    # 实际应使用 RoleBinding 创建用户权限
    # 这里仅为演示返回成功
    return {
        "status": "success",
        "message": f"用户 {user} 被赋予角色 {role}（组织 {org_name}）"
    }

# ✅ 创建环境（示例：部署 Job / Pod / Deployment）
@router.post("/api/org/env/create")
def create_env(org_name: str, job_name: str):
    # TODO: 可添加 Deployment 模板逻辑
    return {
        "status": "success",
        "message": f"{org_name} 中的作业 {job_name} 环境准备完成（占位）"
    }

# ✅ 删除环境
@router.post("/api/org/env/release")
def release_env(org_name: str, job_name: str):
    # TODO: 删除相关资源
    return {
        "status": "success",
        "message": f"{org_name} 中的作业 {job_name} 已释放（占位）"
    }

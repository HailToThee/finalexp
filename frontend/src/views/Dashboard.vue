<template>
  <div>
    <h2>主界面</h2>
    <router-link to="/files">文件管理</router-link> |
    <router-link to="/images">镜像管理</router-link> |
    <router-link to="/orgs">组织管理</router-link> |
    <router-link to="/resources">资源管理</router-link>
    <router-view />
  </div>
</template>
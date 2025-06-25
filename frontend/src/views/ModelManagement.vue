<template>
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold">Model Management</h1>
        <button @click="uploadModel" class="bg-blue-500 text-white px-4 py-2 rounded">Upload Model</button>
    </div>
</template>
<script>
export default {
    methods: {
        async uploadModel() {
            try {
                const response = await this.$axios.post('/api/model/upload', {}, {
                    headers: { Authorization: `Bearer ${this.localStorage.getItem('token')}` }
                })
                console.log(response.data.message)
            } catch (error) {
                console.error('Model upload failed:', error)
            }
        },
    },
    }
</script>
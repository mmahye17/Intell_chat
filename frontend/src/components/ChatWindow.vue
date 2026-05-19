<template>
  <main class="chat-main">
    <header class="chat-header">
      <h3>{{ title || '新对话' }}</h3>
    </header>

    <div class="messages-area" ref="msgArea">
      <div v-if="messages.length === 0 && !loading" class="welcome">
        <h1>RAG 智能对话系统</h1>
        <p>上传文档开始对话，或直接输入问题</p>
      </div>
      <MessageBubble v-for="msg in messages" :key="msg.id" :message="msg" :documents="documents" />
      <div v-if="loading" class="typing-row">
        <el-icon class="is-loading" :size="20"><Loading /></el-icon>
        <span>AI 正在思考...</span>
      </div>
    </div>

    <div class="input-area">
      <div class="file-row" v-if="selectedFile">
        <el-tag closable @close="selectedFile = null" type="info">
          <el-icon><Document /></el-icon> {{ selectedFile.name }}
        </el-tag>
      </div>
      <div class="input-row">
        <el-upload
          :auto-upload="false"
          :show-file-list="false"
          :on-change="onFileChange"
          accept=".txt,.pdf,.csv,.json,.html,.md"
        >
          <el-button circle :icon="Paperclip" />
        </el-upload>

        <el-tooltip content="向量检索" placement="top" :disabled="hybridMode">
          <el-tooltip content="向量+BM25 混合检索" placement="top" :disabled="!hybridMode">
            <el-button
              :type="hybridMode ? 'warning' : 'default'"
              text
              @click="hybridMode = !hybridMode"
              style="font-size:12px"
            >
              {{ hybridMode ? '双检索' : '向量' }}
            </el-button>
          </el-tooltip>
        </el-tooltip>

        <el-input
          v-model="input"
          placeholder="输入消息，Enter 发送"
          @keydown.enter.exact="doSend"
          :disabled="loading"
          size="large"
          class="msg-input"
        />

        <el-button
          type="primary"
          :icon="Promotion"
          :disabled="!input.trim() || loading"
          @click="doSend"
          circle
        />
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Paperclip, Promotion, Loading, Document } from '@element-plus/icons-vue'
import MessageBubble from './MessageBubble.vue'

const props = defineProps({ messages: Array, documents: Array, loading: Boolean, title: String, convId: [Number, String] })
const emit = defineEmits(['send'])
const input = ref('')
const selectedFile = ref(null)
const hybridMode = ref(false)
const msgArea = ref(null)

function onFileChange(file) {
  selectedFile.value = file.raw
}

async function doSend() {
  const text = input.value.trim()
  if (!text) return
  emit('send', { query: text, file: selectedFile.value, retrievalMode: hybridMode.value ? 'hybrid' : 'vector' })
  input.value = ''
  selectedFile.value = null
}

watch(() => props.messages?.length, () => {
  nextTick(() => {
    if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight
  })
})
</script>

<style scoped>
.chat-main { flex: 1; display: flex; flex-direction: column; min-width: 0; background: #f5f6f8; }
.chat-header { padding: 14px 24px; border-bottom: 1px solid #e4e7ed; background: #fff; }
.chat-header h3 { font-size: 16px; font-weight: 500; margin: 0; color: #303133; }
.messages-area { flex: 1; overflow-y: auto; padding: 24px; }
.welcome { text-align: center; margin-top: 120px; }
.welcome h1 { font-size: 28px; margin-bottom: 8px; color: #409eff; }
.welcome p { color: #909399; }
.typing-row { display: flex; align-items: center; gap: 8px; padding: 12px 0; color: #409eff; font-size: 14px; }
.input-area { padding: 16px 24px; border-top: 1px solid #e4e7ed; background: #fff; }
.file-row { margin-bottom: 8px; }
.input-row { display: flex; align-items: center; gap: 8px; }
.msg-input { flex: 1; }
</style>

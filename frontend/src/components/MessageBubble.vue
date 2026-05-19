<template>
  <div :class="['msg-row', msg.role]">
    <el-avatar v-if="msg.role === 'assistant'" :size="32" :icon="ChatLineSquare" style="margin-right:10px" />
    <div :class="['msg-bubble', msg.role]">
      <div class="msg-content" v-html="renderContent(msg.content)"></div>
      <div v-if="files.length > 0" class="msg-files">
        <el-tag
          v-for="f in files"
          :key="f.id"
          size="small"
          :icon="Document"
          type="info"
        >
          {{ f.filename }}
        </el-tag>
      </div>
      <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
    </div>
    <el-avatar v-if="msg.role === 'user'" :size="32" :icon="UserFilled" style="margin-left:10px" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ChatLineSquare, UserFilled, Document } from '@element-plus/icons-vue'

const props = defineProps({ message: Object, documents: Array })
const msg = props.message

const files = computed(() => {
  if (!props.documents || !msg.id) return []
  return props.documents.filter(d => d.message_id === msg.id)
})

function renderContent(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN', { month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' })
}
</script>

<style scoped>
.msg-row { display: flex; margin-bottom: 20px; align-items: flex-start; }
.msg-row.user { justify-content: flex-end; }
.msg-bubble { max-width: 70%; padding: 12px 16px; border-radius: 12px; }
.msg-bubble.user { background: #e6f0ff; color: #303133; }
.msg-bubble.assistant { background: #fff; color: #303133; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.msg-content { font-size: 14px; line-height: 1.6; word-break: break-word; }
.msg-content :deep(code) { background: #f0f2f5; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #e65c5c; }
.msg-content :deep(pre) { background: #f5f6f8; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 8px 0; border: 1px solid #e4e7ed; }
.msg-content :deep(pre code) { background: none; padding: 0; }
.msg-files { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }
.msg-time { font-size: 11px; color: #999; margin-top: 6px; }
</style>

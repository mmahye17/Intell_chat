<template>
  <div class="chat-layout">
    <Sidebar
      :conversations="conversations"
      :active-id="activeConv"
      @select="selectConv"
      @new="startNewChat"
      @delete="handleDeleteConv"
      @rename="handleRenameConv"
    />
    <ChatWindow
      :conv-id="activeConv"
      :messages="messages"
      :documents="documents"
      :loading="sending"
      :title="currentTitle"
      @send="handleSend"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import ChatWindow from '../components/ChatWindow.vue'
import { getConversationList, getConversationDetail, sendMessage, deleteConversation, renameConversation } from '../api/index.js'

const conversations = ref([])
const activeConv = ref(null)
const messages = ref([])
const documents = ref([])
const sending = ref(false)
const currentTitle = ref('新对话')

onMounted(() => fetchConvList())

async function fetchConvList() {
  try {
    const res = await getConversationList()
    const data = res.data?.data || res.data
    conversations.value = Array.isArray(data) ? data : (data?.list || [])
  } catch (e) { /* ignore */ }
}

async function fetchMessages(convId) {
  try {
    const res = await getConversationDetail(convId)
    const d = res.data?.data
    if (d) {
      messages.value = d.messages || []
      documents.value = d.documents || []
      currentTitle.value = d.title || ''
    }
  } catch (e) { /* ignore */ }
}

async function selectConv(conv) {
  activeConv.value = conv.id
  currentTitle.value = conv.title || ''
  await fetchMessages(conv.id)
}

function startNewChat() {
  activeConv.value = null
  messages.value = []
  documents.value = []
  currentTitle.value = '新对话'
}

async function handleSend({ query, file, retrievalMode }) {
  // 先显示用户消息
  const tempMsgId = Date.now()
  messages.value.push({ id: tempMsgId, role: 'user', content: query, created_at: new Date().toISOString() })
  // 有文件立刻显示
  let tempDoc = null
  if (file) {
    tempDoc = { id: tempMsgId, message_id: tempMsgId, filename: file.name }
    documents.value.push(tempDoc)
  }
  sending.value = true
  try {
    const res = await sendMessage(query, activeConv.value, file, retrievalMode)
    const d = res.data?.data
    if (d) {
      if (!activeConv.value) activeConv.value = d.conv_id
      // 替换临时用户消息为后端返回的
      messages.value[messages.value.length - 1] = d.user_message
      if (d.assistant_message) messages.value.push(d.assistant_message)
      // 更新文档的 message_id
      if (tempDoc) {
        tempDoc.message_id = d.user_message.id
        tempDoc.id = d.user_message.id
      }
      currentTitle.value = d.title || currentTitle.value
    }
    await fetchConvList()
  } catch (e) {
    messages.value.pop() // 失败移除临时用户消息
    if (tempDoc) documents.value.pop()
  }
  finally { sending.value = false }
}

async function handleDeleteConv(convId) {
  await deleteConversation(convId)
  if (activeConv.value === convId) startNewChat()
  await fetchConvList()
}

async function handleRenameConv(convId, title) {
  await renameConversation(convId, title)
  await fetchConvList()
}
</script>

<style scoped>
.chat-layout { display: flex; height: 100vh; background: #f5f6f8; }
</style>

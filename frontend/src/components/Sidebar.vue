<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <el-button type="primary" @click="$emit('new')" style="width:100%">
        <el-icon><Plus /></el-icon> 新对话
      </el-button>
    </div>

    <div class="conv-list">
      <div v-for="conv in conversations" :key="conv.id" :class="['conv-item', { active: conv.id === activeId }]"
        @click="$emit('select', conv)">
        <div class="conv-header">
          <span class="conv-title">{{ conv.title || '新对话' }}</span>
          <div class="conv-actions">
            <el-button text size="small" @click.stop="openRename(conv)"><el-icon><Edit /></el-icon></el-button>
            <el-button text size="small" @click.stop="confirmDelete(conv.id)"><el-icon><Delete /></el-icon></el-button>
          </div>
        </div>
        <div class="conv-meta">{{ conv.last_message || '点击查看对话' }}</div>
      </div>
      <div v-if="conversations.length === 0" class="empty">暂无对话，点击上方按钮开始</div>
    </div>

    <div class="sidebar-footer">
      <div class="user-row" @click="openProfile">
        <el-avatar :size="32" :icon="UserFilled" style="cursor:pointer" />
        <span class="username" style="cursor:pointer">{{ user?.username || '用户' }}</span>
        <el-button text size="small" @click.stop="handleLogout">退出</el-button>
      </div>
    </div>

    <el-dialog v-model="renameVisible" title="重命名会话" width="360px">
      <el-input v-model="renameValue" placeholder="输入新标题" @keyup.enter="confirmRename" />
      <template #footer>
        <el-button @click="renameVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="profileVisible" title="个人信息" width="400px">
      <el-form v-if="profile" label-position="top">
        <el-form-item label="用户名"><el-input :model-value="profile.username" disabled /></el-form-item>
        <el-form-item label="昵称"><el-input v-model="profile.nickname" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="profile.gender" style="width:100%">
            <el-option label="男" value="male" /><el-option label="女" value="female" /><el-option label="保密" value="" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱"><el-input v-model="profile.email" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { authStore } from '../stores/auth.js'
import { logout, getUserInfo, updateUserInfo } from '../api/index.js'

defineProps({ conversations: Array, activeId: [Number, String] })
const emit = defineEmits(['select', 'new', 'delete', 'rename'])
const router = useRouter()
const user = authStore.user
const renameVisible = ref(false)
const renameValue = ref('')
const renameConv = ref(null)
const profileVisible = ref(false)
const profile = ref(null)
const saving = ref(false)

function getUserId() {
  const token = authStore.token
  if (!token) return null
  try { const p = JSON.parse(atob(token.split('.')[1])); return parseInt(p.sub) } catch { return null }
}
async function openProfile() {
  const uid = getUserId(); if (!uid) return
  try { const r = await getUserInfo(uid); profile.value = r.data?.data || r.data; profileVisible.value = true } catch { ElMessage.error('获取信息失败') }
}
async function saveProfile() {
  saving.value = true
  try {
    await updateUserInfo({ username: profile.value.username, nickname: profile.value.nickname, gender: profile.value.gender, email: profile.value.email })
    ElMessage.success('保存成功'); profileVisible.value = false
  } catch { } finally { saving.value = false }
}
function openRename(conv) { renameConv.value = conv; renameValue.value = conv.title || ''; renameVisible.value = true }
function confirmRename() { if (renameConv.value && renameValue.value.trim()) emit('rename', renameConv.value.id, renameValue.value.trim()); renameVisible.value = false }
async function confirmDelete(convId) { try { await ElMessageBox.confirm('确定删除？', '确认删除', { type: 'warning' }); emit('delete', convId) } catch { } }
async function handleLogout() { try { await logout() } catch { } authStore.clearAuth(); router.push('/login') }
</script>

<style scoped>
.sidebar { width: 280px; min-width: 280px; background: #fff; display: flex; flex-direction: column; border-right: 1px solid #e4e7ed; }
.sidebar-header { padding: 16px; }
.conv-list { flex: 1; overflow-y: auto; padding: 0 8px; }
.conv-item { padding: 12px; border-radius: 8px; cursor: pointer; margin-bottom: 2px; }
.conv-item:hover { background: #f0f2f5; }
.conv-item.active { background: #e6f0ff; }
.conv-header { display: flex; justify-content: space-between; align-items: center; }
.conv-title { font-size: 14px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; color: #303133; }
.conv-actions { display: none; gap: 2px; }
.conv-item:hover .conv-actions { display: flex; }
.conv-meta { font-size: 12px; color: #999; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.empty { text-align: center; color: #999; margin-top: 40px; font-size: 13px; }
.sidebar-footer { padding: 16px; border-top: 1px solid #e4e7ed; }
.user-row { display: flex; align-items: center; gap: 8px; }
.username { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #303133; }
</style>

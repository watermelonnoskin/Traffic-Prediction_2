<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- 左侧装饰区域 -->
      <div class="auth-decoration">
        <div class="decoration-content">
          <h1>欢迎回来</h1>
          <p>登录您的账户，开始探索交通数据可视化系统</p>
          <div class="decoration-icons">
            <div class="icon-circle">🚗</div>
            <div class="icon-circle">📊</div>
            <div class="icon-circle">🎯</div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区域 -->
      <div class="auth-form">
        <div class="form-header">
          <h2>{{ isLogin ? '登录' : '注册' }}</h2>
          <p>{{ isLogin ? '欢迎回来，请登录您的账户' : '创建新账户，开始您的旅程' }}</p>
        </div>

        <!-- 登录表单 -->
        <form v-if="isLogin" @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="login-username">用户名</label>
            <input
              id="login-username"
              v-model="loginForm.username"
              type="text"
              placeholder="请输入用户名"
              :class="{ 'error': errors.loginUsername }"
              @blur="validateLoginUsername"
            />
            <span class="error-message" v-if="errors.loginUsername">{{ errors.loginUsername }}</span>
          </div>

          <div class="form-group">
            <label for="login-password">密码</label>
            <input
              id="login-password"
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :class="{ 'error': errors.loginPassword }"
              @blur="validateLoginPassword"
            />
            <span class="error-message" v-if="errors.loginPassword">{{ errors.loginPassword }}</span>
          </div>

          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="loginForm.remember" />
              <span>记住我</span>
            </label>
            <a href="#" class="forgot-password">忘记密码？</a>
          </div>

          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            <span v-if="!isSubmitting">登录</span>
            <span v-else>登录中...</span>
          </button>
        </form>

        <!-- 注册表单 -->
        <form v-else @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label for="register-username">用户名</label>
            <input
              id="register-username"
              v-model="registerForm.username"
              type="text"
              placeholder="请输入用户名"
              :class="{ 'error': errors.registerUsername }"
              @blur="validateRegisterUsername"
            />
            <span class="error-message" v-if="errors.registerUsername">{{ errors.registerUsername }}</span>
          </div>

          <div class="form-group">
            <label for="register-password">密码</label>
            <input
              id="register-password"
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码（至少6位）"
              :class="{ 'error': errors.registerPassword }"
              @blur="validateRegisterPassword"
            />
            <span class="error-message" v-if="errors.registerPassword">{{ errors.registerPassword }}</span>
            <div class="password-strength">
              <div class="strength-bar" :class="passwordStrengthClass"></div>
            </div>
          </div>

          <div class="form-group">
            <label for="register-confirm">确认密码</label>
            <input
              id="register-confirm"
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              :class="{ 'error': errors.registerConfirm }"
              @blur="validateRegisterConfirm"
            />
            <span class="error-message" v-if="errors.registerConfirm">{{ errors.registerConfirm }}</span>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="registerForm.agree" />
              <span>我已阅读并同意 <a href="#" class="link">服务条款</a> 和 <a href="#" class="link">隐私政策</a></span>
            </label>
            <span class="error-message" v-if="errors.agree">{{ errors.agree }}</span>
          </div>

          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            <span v-if="!isSubmitting">注册</span>
            <span v-else>注册中...</span>
          </button>
        </form>

        <!-- 切换登录/注册 -->
        <div class="switch-auth">
          <p>
            {{ isLogin ? '还没有账户？' : '已有账户？' }}
            <a href="#" @click.prevent="toggleAuthMode" class="switch-link">
              {{ isLogin ? '立即注册' : '立即登录' }}
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['login-success'])

// 表单状态
const isLogin = ref(true)
const isSubmitting = ref(false)

// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  remember: false
})

// 注册表单数据
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  agree: false
})

// 错误信息
const errors = ref({
  loginUsername: '',
  loginPassword: '',
  registerUsername: '',
  registerPassword: '',
  registerConfirm: '',
  agree: ''
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = registerForm.value.password
  if (!password) return 0
  let strength = 0
  if (password.length >= 6) strength += 1
  if (password.length >= 10) strength += 1
  if (/[A-Z]/.test(password)) strength += 1
  if (/[0-9]/.test(password)) strength += 1
  if (/[^A-Za-z0-9]/.test(password)) strength += 1
  return strength
})

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 1) return 'weak'
  if (strength <= 3) return 'medium'
  return 'strong'
})

// 切换登录/注册模式
const toggleAuthMode = () => {
  isLogin.value = !isLogin.value
  // 清空错误信息
  errors.value = {
    loginUsername: '',
    loginPassword: '',
    registerUsername: '',
    registerPassword: '',
    registerConfirm: '',
    agree: ''
  }
}

// 登录验证
const validateLoginUsername = () => {
  if (!loginForm.value.username) {
    errors.value.loginUsername = '请输入用户名'
  } else if (loginForm.value.username.length < 3) {
    errors.value.loginUsername = '用户名至少3个字符'
  } else {
    errors.value.loginUsername = ''
  }
}

const validateLoginPassword = () => {
  if (!loginForm.value.password) {
    errors.value.loginPassword = '请输入密码'
  } else if (loginForm.value.password.length < 6) {
    errors.value.loginPassword = '密码至少6个字符'
  } else {
    errors.value.loginPassword = ''
  }
}

// 注册验证
const validateRegisterUsername = () => {
  if (!registerForm.value.username) {
    errors.value.registerUsername = '请输入用户名'
  } else if (registerForm.value.username.length < 3) {
    errors.value.registerUsername = '用户名至少3个字符'
  } else if (!/^[a-zA-Z0-9_]+$/.test(registerForm.value.username)) {
    errors.value.registerUsername = '用户名只能包含字母、数字和下划线'
  } else {
    errors.value.registerUsername = ''
  }
}

const validateRegisterPassword = () => {
  if (!registerForm.value.password) {
    errors.value.registerPassword = '请输入密码'
  } else if (registerForm.value.password.length < 6) {
    errors.value.registerPassword = '密码至少6个字符'
  } else {
    errors.value.registerPassword = ''
  }
  // 如果确认密码已输入，重新验证确认密码
  if (registerForm.value.confirmPassword) {
    validateRegisterConfirm()
  }
}

const validateRegisterConfirm = () => {
  if (!registerForm.value.confirmPassword) {
    errors.value.registerConfirm = '请确认密码'
  } else if (registerForm.value.confirmPassword !== registerForm.value.password) {
    errors.value.registerConfirm = '两次输入的密码不一致'
  } else {
    errors.value.registerConfirm = ''
  }
}

// 处理登录
const handleLogin = async () => {
  validateLoginUsername()
  validateLoginPassword()

  if (errors.value.loginUsername || errors.value.loginPassword) {
    return
  }

  isSubmitting.value = true

  try {
    // 模拟登录请求
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 这里添加实际的登录逻辑
    console.log('登录信息:', loginForm.value)
    
    // 登录成功，触发事件
    emit('login-success')
  } catch (error) {
    console.error('登录失败:', error)
    alert('登录失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  validateRegisterUsername()
  validateRegisterPassword()
  validateRegisterConfirm()

  if (!registerForm.value.agree) {
    errors.value.agree = '请同意服务条款和隐私政策'
  } else {
    errors.value.agree = ''
  }

  if (errors.value.registerUsername || errors.value.registerPassword || 
      errors.value.registerConfirm || errors.value.agree) {
    return
  }

  isSubmitting.value = true

  try {
    // 模拟注册请求
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 这里添加实际的注册逻辑
    console.log('注册信息:', registerForm.value)
    alert('注册成功！请登录')
    
    // 注册成功后切换到登录
    isLogin.value = true
    registerForm.value = {
      username: '',
      password: '',
      confirmPassword: '',
      agree: false
    }
  } catch (error) {
    console.error('注册失败:', error)
    alert('注册失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

.auth-card {
  display: flex;
  background: white;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  max-width: 900px;
  width: 100%;
  min-height: 600px;
}

/* 左侧装饰区域 */
.auth-decoration {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.decoration-content h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
}

.decoration-content p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 40px;
  line-height: 1.6;
}

.decoration-icons {
  display: flex;
  gap: 20px;
  margin-top: 40px;
}

.icon-circle {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  backdrop-filter: blur(10px);
}

/* 右侧表单区域 */
.auth-form {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header {
  margin-bottom: 40px;
}

.form-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 10px;
}

.form-header p {
  color: #7f8c8d;
  font-size: 1rem;
}

/* 表单样式 */
.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.9rem;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e8ecf1;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  outline: none;
  box-sizing: border-box;
}

.form-group input[type="text"]:focus,
.form-group input[type="password"]:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input[type="text"].error,
.form-group input[type="password"].error {
  border-color: #ef4444;
}

.error-message {
  display: block;
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 6px;
  font-weight: 500;
}

/* 密码强度 */
.password-strength {
  margin-top: 8px;
  height: 4px;
  background: #e8ecf1;
  border-radius: 2px;
  overflow: hidden;
}

.strength-bar {
  height: 100%;
  width: 0%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-bar.weak {
  width: 33%;
  background: #ef4444;
}

.strength-bar.medium {
  width: 66%;
  background: #f59e0b;
}

.strength-bar.strong {
  width: 100%;
  background: #10b981;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label .link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.checkbox-label .link:hover {
  text-decoration: underline;
}

.forgot-password {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 切换登录/注册 */
.switch-auth {
  margin-top: 30px;
  text-align: center;
}

.switch-auth p {
  color: #7f8c8d;
  font-size: 0.95rem;
}

.switch-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
}

.switch-link:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .auth-card {
    flex-direction: column;
    min-height: auto;
  }
  
  .auth-decoration {
    padding: 40px 30px;
  }
  
  .decoration-content h1 {
    font-size: 2rem;
  }
  
  .decoration-content p {
    font-size: 1rem;
  }
  
  .auth-form {
    padding: 40px 30px;
  }
  
  .form-header h2 {
    font-size: 1.5rem;
  }
}
</style>

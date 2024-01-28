
'use client'
import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
export default function Register () {
  const [countdown, setCountdown] = useState(0)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone_number: '',
    password: '',
    verification_code: '',
  })
  const [errors, setErrors] = useState({})
  const router = useRouter()
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }))
    if (errors[name]) {
      setErrors((prevErrors) => ({
        ...prevErrors,
        [name]: null,
      }))
    }
  }
  const backend = process.env.NEXT_PUBLIC_BACK_END
  const handleRegister = async () => {
    const { confirmPassword, ...dataToSubmit } = formData
    const endpoint = backend + '/users/register' // 替换为您的API端点
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSubmit) // 将表单数据作为payload发送
      })

      const data = await response.json()

      if (response.ok) {
        // 注册成功，处理返回的数据，例如保存token或跳转到登录页
        alert('注册成功')

        router.push('./login')
      } else {

        // 注册失败，处理错误，例如显示错误消息
        alert('Registration failed:', data)
        // 这里可以设置错误信息以显示在表单上
        setErrors(data.errors || {})


      }
    } catch (error) {
      // 网络或其他错误，处理异常
      alert('Error:', error)


    }
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    // 可以在这里添加表单验证逻辑
    handleRegister() // 调用注册处理函数
  }
  const [sendingCode, setSendingCode] = useState(false)

  const sendVerificationCode = async () => {
    setSendingCode(true)
    const queryParams = new URLSearchParams({ mobile: formData.phone_number })
    const url = `${backend}/users/send_verify_code?${queryParams}`

    try {
      const response = await fetch(url, {
        method: 'POST', // 使用POST方法
        headers: {
          'accept': 'application/json', // 指定期望的响应格式为JSON
        },
        // 由于 '-d' 是空的，这里不需要设置body属性
      })

      const data = await response.json()

      if (response.ok) {
        // 验证码发送成功，处理返回的数据
        alert('验证码发送成功')
        console.log('Verification code sent:', data)
        // 可能需要在这里处理验证码发送状态的显示，例如启动倒计时等
      } else {
        // 验证码发送失败，处理错误
        alert('该手机号已注册')
        console.error('Failed to send verification code:', data)
      }
    } catch (error) {
      // 网络或其他错误，处理异常
      console.error('Error:', error)
    }
    setCountdown(60)
    setSendingCode(false)
  }

  const validateForm = () => {
    let isValid = true
    let newErrors = {}

    // Email validation
    if (!formData.email) {
      isValid = false
      newErrors.email = '请输入邮箱地址。'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      isValid = false
      newErrors.email = '请输入有效的邮箱地址。'
    }

    // Password complexity validation
    // const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/
    // if (!passwordRegex.test(formData.password)) {
    //   isValid = false
    //   newErrors.password = '密码至少包含8个字符，且必须包含数字、大小写字母。'
    // }

    // Confirm password validation
    if (formData.password !== formData.confirmPassword) {
      isValid = false
      newErrors.confirmPassword = '两次输入的密码不匹配。'
    }

    setErrors(newErrors)
    return isValid
  }
  useEffect(() => {
    let timer
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000)
    }
    return () => clearTimeout(timer)
  }, [countdown])

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="card w-full max-w-xl bg-base-100 shadow-2xl">
        <div className="card-body">
          <h2 className="card-title text-2xl">注册账号</h2>
          <p className="mb-5 text-gray-600">使用邮箱注册新账号</p>
          <form onSubmit={handleSubmit}>
            {/* Username field */}
            <div className="form-control">
              <label className="label">
                <span className="label-text">用户名</span>
              </label>
              <input
                type="text"
                name="username"
                placeholder="用户名"
                className="input input-bordered"
                value={formData.username}
                onChange={handleChange}
              />
            </div>

            {/* Email field */}
            <div className="form-control">
              <label className="label">
                <span className="label-text">邮箱地址</span>
              </label>
              <input
                type="email"
                name="email"
                placeholder="user@example.com"
                className="input input-bordered"
                value={formData.email}
                onChange={handleChange}
              />
              {errors.email && <span className="text-error text-xs">{errors.email}</span>}
            </div>

            {/* Phone field */}
            <div className="form-control">
              <label className="label">
                <span className="label-text">手机号码</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  name="phone_number"
                  placeholder="11位手机号"
                  className="input input-bordered w-full pr-20"
                  value={formData.phone_number}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="absolute top-0 right-0 rounded-l-none btn btn-primary"
                  onClick={sendVerificationCode}
                  disabled={countdown > 0}
                >
                  {countdown > 0 ? `重新获取 (${countdown}s)` : '获取验证码'}
                </button>
              </div>
            </div>

            {/* Password field */}
            <div className="form-control">
              <label className="label">
                <span className="label-text">设置密码</span>
              </label>
              <input
                type="password"
                name="password"
                placeholder="********"
                className="input input-bordered"
                value={formData.password}
                onChange={handleChange}
              />
              {errors.password && <span className="text-error text-xs">{errors.password}</span>}
            </div>

            {/* Confirm Password field */}
            <div className="form-control">
              <label className="label">
                <span className="label-text">确认密码</span>
              </label>
              <input
                type="password"
                name="confirmPassword"
                placeholder="********"
                className="input input-bordered"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
              {errors.confirmPassword && <span className="text-error text-xs">{errors.confirmPassword}</span>}
            </div>

            {/* Verification Code field */}
            <div className="form-control">
              <label className="label">
                <span className="label-text">验证码</span>
              </label>
              <input
                type="text" // 使用 type="text" 来接受验证码输入
                name="verification_code"
                placeholder="短信验证码"
                className="input input-bordered"
                value={formData.verification_code}
                onChange={handleChange}
              />
            </div>

            {/* Submit button */}
            <div className="form-control mt-6">
              <button type="submit" className="btn btn-primary">立即注册</button>
            </div>
          </form>

          {/* Link to sign in */}
          <div className="text-center mt-4">
            <Link href="/login" legacyBehavior>
              <a className="link link-primary">已有账号？立即登录</a>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )

}
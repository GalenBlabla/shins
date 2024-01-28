"use client"

import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
export default function Login () {
  const router = useRouter()
  const [loginMethod, setLoginMethod] = useState('password')
  const [account, setAccount] = useState('')
  const [password, setPassword] = useState('')
  const [verificationCode, setVerificationCode] = useState('')
  const [sendingCode, setSendingCode] = useState(false)
  const backend = process.env.NEXT_PUBLIC_BACK_END
  const sendVerificationCode = async () => {
    setSendingCode(true)
    const queryParams = new URLSearchParams({ mobile: account })
    const url = `${backend}/users/send_verify_code?${queryParams}`

    try {
      const response = await fetch(url, {
        method: 'POST', // 使用POST方法
        headers: {

          'Content-Type': 'application/json'
        }
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
        console.error('Failed to send verification code:', data)
      }
    } catch (error) {
      // 网络或其他错误，处理异常
      console.error('Error:', error)
    }

    setSendingCode(false)
  }
  const handleLogin = async (event) => {
    event.preventDefault() // 防止页面刷新
    const backend = process.env.NEXT_PUBLIC_BACK_END
    const endpoint = backend + '/users/login' // API端点
    const payload = {
      login: account,
      password: password,
      verification_code: verificationCode, // 确保你的后端能接受这个字段
    }

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      const data = await response.json()
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('token_type', data.token_type)
        router.push('./bind')
      }
      if (response.ok) {
        // 登录成功，处理返回的数据，例如保存token
        console.log('Login successful:', data)
      } else {
        // 登录失败，处理错误
        console.error('Login failed:', data)
      }
    } catch (error) {
      // 网络或其他错误，处理异常
      console.error('Error:', error)
    }
  }

  return (
    // ... 省略其它代码 ...
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="p-10 bg-white rounded-lg shadow-xl w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-2 text-gray-800">登录</h2>
        <p className="text-gray-600 mb-8">使用邮箱或者手机登录</p>

        <div className="mb-4">
          <label className="block text-gray-700"

          >账号</label>
          <input type="email" placeholder="user@acme.com" className="input input-bordered w-full" value={account}
            onChange={(e) => setAccount(e.target.value)} />
        </div>
        {loginMethod === 'password' ? (
          <form onSubmit={handleLogin}>
            <div className="mb-6">
              <label className="block text-gray-700">密码</label>
              <input
                type="password"
                placeholder="********"
                className="input input-bordered w-full"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary w-full mb-2">登录</button>
            <a href="#" className="text-sm text-primary block text-center">忘记密码?</a>
          </form>
        ) : (
          <form onSubmit={handleLogin}>
            <div className="mb-6">
              <label className="block text-gray-700">短信验证码</label>

              <input
                type="text"
                placeholder="123456"
                className="input input-bordered w-full"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}

              />

            </div>
            <button
              type="button"
              className="btn btn-primary w-full mb-2"
              onClick={sendVerificationCode}
              disabled={sendingCode}
            >
              {sendingCode ? '发送中...' : '获取验证码'}
            </button>
            <button type="submit" className="btn btn-primary w-full mb-2">登录</button>

          </form>
        )}

        <div className="flex items-center justify-between mt-8">
          <button
            className="text-sm text-gray-600 hover:text-gray-800"
            onClick={() => setLoginMethod(loginMethod === 'password' ? 'sms' : 'password')}
          >
            {loginMethod === 'password' ? '验证码登录' : '密码登录'}
          </button>
          <Link href="./register">
            免费注册
          </Link>
        </div>
      </div>
    </div>
    // ... 省略其它代码 ...
  )
}

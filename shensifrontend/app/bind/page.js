// pages/bind-key.js
'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
export default function BindKeyPage () {
  const [key, setKey] = useState('')
  const router = useRouter()
  const [accessToken, setAccessToken] = useState('')
  const [tokenType, setTokenType] = useState('')
  useEffect(() => {
    // 由于 useEffect 只在客户端执行，因此可以安全地访问 localStorage
    const storedAccessToken = localStorage.getItem('access_token')
    const storedTokenType = localStorage.getItem('token_type')
    setAccessToken(storedAccessToken)
    setTokenType(storedTokenType)
  }, [])
  const backend = process.env.NEXT_PUBLIC_BACK_END
  const handleSubmit = async (event) => {
    event.preventDefault()
    const authHeader = `${tokenType} ${accessToken}`
    try {
      const response = await fetch(backend + '/bind-key/', {
        method: 'POST',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key }),
      })

      if (response.ok) {
        // 密钥绑定成功，跳转到新的页面
        router.push('/write')
      } else {
        // 处理错误情况，例如显示一个错误消息
        console.error('Failed to bind key')
      }
    } catch (error) {
      // 处理网络错误
      console.error('There was an error submitting the form:', error)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="form-control w-full max-w-xs mx-auto my-10">
        <label htmlFor="key" className="label">
          <span className="label-text">输入你的key:</span>
        </label>
        <input
          type="text"
          id="key"
          name="key"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          required
          className="input input-bordered w-full max-w-xs"
        />
        <button type="submit" className="btn btn-primary mt-4">
          绑定
        </button>




      </form>
      <Link href={'/write'}>
        <button className="flex btn btn-primary mt-4  w-full max-w-xs mx-auto my-10">

          稍后绑定

        </button>
      </Link>
    </div>



  )
}